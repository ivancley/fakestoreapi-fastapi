from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

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
from api.v1.fakestoreapi.services.produto_async import ProductService
from api.v1.favorite.mapper import mapper_favorite_to_favorite_response
from api.v1.user.service import UserService


class FavoriteService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.serviceProduct = ProductService(db)
        self.serviceUser = UserService(db)

    async def list(
        self,
        skip: int = 0,
        limit: int = 10,
        favorite_filter: FavoriteFilter = None,
        current_user: User = None
    ) -> List[FavoriteResponse]:

        if "ADMIN"  in current_user.permissions:
            query = select(Favorite).where(Favorite.flg_deleted == False)
        else:
            query = select(Favorite).where(
                Favorite.flg_deleted == False, 
                Favorite.user_id == current_user.id
            )
        
        if favorite_filter:
            query = favorite_filter.filter(query)
            query = favorite_filter.sort(query)
        
        if favorite_filter is None or not favorite_filter.order_by:
            query = query.order_by(Favorite.created_at.desc())

        result = await self.db.execute(query.offset(skip).limit(limit))
        favorites = result.scalars().all()

        return favorites


    async def get(self, id: UUID, current_user: User) -> FavoriteResponse:   

        if "ADMIN" in current_user.permissions:
            query = select(Favorite).where(
                Favorite.flg_deleted == False,
                Favorite.id == id
            )
        else:
            query = select(Favorite).where(
                Favorite.id == id,
                Favorite.flg_deleted == False,
                Favorite.user_id == current_user.id
            )

        result = await self.db.execute(query)
        favorite = result.scalar_one_or_none()
        
        if not favorite:
            raise exception_404_NOT_FOUND(detail=f"Favorito com ID {id} não encontrado")
        
        return favorite
    
    async def favorite_exists(self, product_id: UUID, current_user: User) -> bool:
        query = select(Favorite).where(
            Favorite.product_id == product_id,
            Favorite.flg_deleted == False,
            Favorite.user_id == current_user.id
        )
        result = await self.db.execute(query)
        favorite = result.scalar_one_or_none()
        
        return favorite is not None


    async def create(self, favorite: FavoriteCreate, current_user: User) -> FavoriteResponse:
        product = await self.serviceProduct.get_by_id_api(favorite.api_id)

        if await self.favorite_exists(product.id, current_user):
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
            await self.db.commit()
            await self.db.refresh(new_favorite)

        except IntegrityError as e:
            await self.db.rollback()
            raise exception_400_BAD_REQUEST(detail=f"Erro ao criar favorito: {str(e)}")

        return new_favorite

    async def update(self, favorite: FavoriteUpdate, current_user: User) -> FavoriteResponse:
        query = select(Favorite).where(
            Favorite.id == favorite.id,
            Favorite.flg_deleted == False,
            Favorite.user_id == current_user.id
        )
        result = await self.db.execute(query)
        existing_favorite = result.scalar_one_or_none()
        
        if not existing_favorite:
            raise exception_404_NOT_FOUND(
                detail=f"Favorito com ID {favorite.id} não encontrado"
            )
        
        update_data = favorite.model_dump(exclude_none=True, exclude={"id"})
        
        for field, value in update_data.items():
            setattr(existing_favorite, field, value)
        
        await self.db.commit()
        await self.db.refresh(existing_favorite)
        
        return mapper_favorite_to_favorite_response(existing_favorite)

    async def delete(self, id: UUID, current_user: User) -> FavoriteResponse:

        favorite = await self.get(id, current_user)
        
        favorite.flg_deleted = True
        await self.db.commit()
        
        return favorite