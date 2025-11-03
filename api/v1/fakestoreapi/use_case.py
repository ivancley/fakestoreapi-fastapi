from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from api.v1._shared.schemas import ProductResponse
from api.v1.fakestoreapi.mapper import (
    mapper_list_products_to_list_dict,
    mapper_product_to_dict,
)
from api.v1.fakestoreapi.services.api import APIService
from api.v1.fakestoreapi.services.background_task import (
    save_or_update_product_task,
    save_or_update_products_in_database_sql_task,
)
from api.v1.fakestoreapi.services.background_task import get_products_api
from api.v1.fakestoreapi.services.redis import RedisService
from api.v1.fakestoreapi.services.produto_async import ProductService
from api.utils.exceptions import exception_404_NOT_FOUND

class ProductUseCase:

    def __init__(self, db: AsyncSession):
        self.serviceSQL = ProductService(db)
        self.serviceAPI = APIService()
        self.serviceRedis = RedisService()

    async def list(self) -> List[ProductResponse]:
        """
        Estratégia adotada:
        1 Tenta buscar na Redis
        2 Caso não encontre, tenta buscar na API externa e atualizar banco em background
        3 Se API falhar, continua e retorna produtos do banco local    
        """
        products = []
        products_redis = await self.serviceRedis.get_all()
        if products_redis:
            get_products_api.delay()
            return products_redis
        
        try:
            # Buscar produtos da API para atualizar banco em background
            products = await self.serviceAPI.list()
            if products:
                products_dict = mapper_list_products_to_list_dict(products)
                save_or_update_products_in_database_sql_task.delay(products_dict)
                await self.serviceRedis.create_or_update_all(products)

        except Exception:
            # Se API falhar, continuar e retornar do banco local
            return await self.serviceSQL.list()
        
        # Sempre retornar produtos do banco local
        return products

    async def get(self, id: int) -> ProductResponse:
        """
        Estratégia semelhante a anterior porem com foco em um produto específico: 
        1 Tenta buscar na Redis
        2 Caso não encontre, tenta buscar na API externa e atualizar banco em background
        3 Se API falhar, continua e retorna produto do banco local    
        """

        product = await self.serviceRedis.get(id)
        if product:
            product_dict = mapper_product_to_dict(product)
            save_or_update_product_task.delay(product_dict)
            await self.serviceRedis.create_or_update(id, product)
            return product

        try: 
            product = await self.serviceAPI.get(id)
            if product:
                product_dict = mapper_product_to_dict(product)
                save_or_update_product_task.delay(product_dict)
                await self.serviceRedis.create_or_update(id, product)
                return product
        except Exception:
            pass 

        try:
            product = await self.serviceSQL.get_by_id_api(id)
            return await self.serviceSQL.get(id)
        
        except Exception:
            raise exception_404_NOT_FOUND(detail=f"Produto com ID {id} não encontrado")
