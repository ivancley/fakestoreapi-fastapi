from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api.utils.exceptions import (
    exception_400_BAD_REQUEST,
    exception_404_NOT_FOUND,
)
from api.v1._shared.models import User, Favorite
from api.v1._shared.schemas import (
    FavoriteResponse,
    FavoriteFilter,
    FavoriteCreate,
    FavoriteUpdate,
    FavoriteDelete,
)
from api.v1.fakestoreapi.services.sql import ProductService


class FavoriteService:

    def __init__(self, db: Session):
        self.db = db
        self.serviceProduct = ProductService(db)

    def list(
        self,
        skip: int = 0,
        limit: int = 10,
        favorite_filter: FavoriteFilter = None,
        current_user: User = None
    ) -> List[FavoriteResponse]:
        
        query = select(Favorite).where(
            Favorite.flg_deleted == False, 
            Favorite.user_id == current_user.id
        )

        if favorite_filter:
            query = favorite_filter.filter(query)
            query = favorite_filter.sort(query)
        
        if favorite_filter is None or not favorite_filter.order_by:
            query = query.order_by(Favorite.created_at.desc())

        result = self.db.execute(query.offset(skip).limit(limit))
        favorites = result.scalars().all()

        return favorites


    def get(self, id: UUID, current_user: User) -> FavoriteResponse:    
        query = select(Favorite).where(
            Favorite.id == id,
            Favorite.flg_deleted == False,
            Favorite.user_id == current_user.id
        )
        result = self.db.execute(query)
        favorite = result.scalar_one_or_none()
        
        if not favorite:
            raise exception_404_NOT_FOUND(detail=f"Favorito com ID {id} não encontrado")
        
        return favorite
    
    def favorite_exists(self, product_id: UUID, current_user: User) -> bool:
        query = select(Favorite).where(
            Favorite.product_id == product_id,
            Favorite.flg_deleted == False,
            Favorite.user_id == current_user.id
        )
        result = self.db.execute(query)
        favorite = result.scalar_one_or_none()
        
        return favorite is not None


    def create(self, favorite: FavoriteCreate, current_user: User) -> FavoriteResponse:
        product = self.serviceProduct.get_by_id_api(favorite.api_id)

        if self.favorite_exists(product.id, current_user):
            raise exception_400_BAD_REQUEST(
                detail=f"Favorito com produto ID {favorite.api_id} já existe"
            )
        
        new_favorite = Favorite(
            user_id=current_user.id,
            product_id=product.id,
            review=favorite.review
        )
        try:
            self.db.add(new_favorite)
            self.db.commit()
            self.db.refresh(new_favorite)

        except IntegrityError as e:
            self.db.rollback()
            raise exception_400_BAD_REQUEST(detail=f"Erro ao criar favorito: {str(e)}")

        return new_favorite

    def update(self, obj: FavoriteUpdate, current_user: User) -> FavoriteResponse:
        query = select(Favorite).where(
            Favorite.id == obj.id,
            Favorite.flg_deleted == False,
            Favorite.user_id == current_user.id
        )
        result = self.db.execute(query)
        favorite = result.scalar_one_or_none()
        
        if not favorite:
            raise exception_404_NOT_FOUND(
                detail=f"Favorito com ID {obj.id} não encontrado"
            )
        
        update_data = obj.model_dump(exclude_none=True, exclude={"id"})
        
        for field, value in update_data.items():
            setattr(favorite, field, value)
        
        self.db.commit()
        self.db.refresh(favorite)
        
        return favorite

    def delete(self, obj: FavoriteDelete, current_user: User) -> FavoriteResponse:

        favorite = self.get(obj.id, current_user)
        
        favorite.flg_deleted = True
        self.db.commit()
        
        return favorite