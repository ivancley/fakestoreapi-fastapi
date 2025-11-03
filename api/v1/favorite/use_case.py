from typing import List
from uuid import UUID

from sqlalchemy.orm import Session

from api.v1._shared.schemas import (
    FavoriteDelete,
    FavoriteFilter,
    FavoriteResponse,
    FavoriteUpdate,
    FavoriteCreate,
    User,
)
from api.v1.favorite.service import FavoriteService
from api.v1.fakestoreapi.services.redis import RedisService
from api.v1.fakestoreapi.services.api import APIService
from api.v1.fakestoreapi.services.sql import ProductService
from api.utils.exceptions import exception_404_NOT_FOUND
from api.v1.favorite.mapper import mapper_favorite_to_favorite_response

class FavoriteUseCase:

    def __init__(self, db: Session):
        self.serviceFavorite = FavoriteService(db)
        self.serviceProduct = ProductService(db)
        self.serviceRedis = RedisService()
        self.serviceAPI = APIService()

    async def list(
        self,
        skip: int = 0,
        limit: int = 10,
        favorite_filter: FavoriteFilter = None,
        current_user: User = None
    ) -> List[FavoriteResponse]:
        favorites = self.serviceFavorite.list(
            skip=skip,
            limit=limit,
            favorite_filter=favorite_filter,
            current_user=current_user)
        return [mapper_favorite_to_favorite_response(favorite) for favorite in favorites]

    async def get(self, id: UUID, current_user: User) -> FavoriteResponse:
        favorite = self.serviceFavorite.get(id, current_user)
        return mapper_favorite_to_favorite_response(favorite)

    async def create(self, favorite: FavoriteCreate, current_user: User) -> FavoriteResponse:
        """
        Antes de salvar o novo favorito verifica se ele existe
        1 buscar no Redis
        2 buscar na API externa
        3 buscar no banco de dados
        """
        # verificar no Redis se o produto já existe
        product_exists = False
        product = await self.serviceRedis.get(id)
        if product:
            product_exists = True
        
        else: 
            # Verificar na API:
            try:
                product = await self.serviceAPI.get(favorite.api_id)
                if product:
                    product_exists = True

            except Exception:
                # Verifica no banco SQL local
                product =  self.serviceProduct.get_by_id_api(favorite.api_id)
                if product:
                    product_exists = True
        
        if product_exists:
            favorite = self.serviceFavorite.create(favorite, current_user)
            return mapper_favorite_to_favorite_response(favorite)
        else:
            raise exception_404_NOT_FOUND(detail=f"Produto com ID {favorite.api_id} não encontrado")

    async def update(self, favorite: FavoriteUpdate, current_user: User) -> FavoriteResponse:
        new_favorite = self.serviceFavorite.update(favorite, current_user)
        return mapper_favorite_to_favorite_response(new_favorite)

    async def delete(self, favorite: FavoriteDelete, current_user: User) -> FavoriteResponse:
        deleted_favorite = self.serviceFavorite.delete(favorite, current_user)
        return mapper_favorite_to_favorite_response(deleted_favorite)
