import json
from typing import List, Optional
from decouple import config
from redis.asyncio import Redis
from api.v1._shared.schemas import ProductResponse
from api.v1.fakestoreapi.mapper import mapper_product_to_dict, mapper_dict_to_product
import logging

REDIS_URL = config("REDIS_URL")
TTL_SECONDS = int(config("REDIS_TTL"))


class RedisService:
    
    def __init__(self):
        self.r = Redis.from_url(REDIS_URL, decode_responses=True)
        self.model = ProductResponse
        self.keyspace = "product"
    
    def _get_key(self, id_api: int) -> str:
        return f"{self.keyspace}:{id_api}"
    
    async def create_or_update(self, id_api: int, product: ProductResponse) -> bool:
        try:
            logging.info(f"Salvando produto {id_api} no Redis")
            product_dict = mapper_product_to_dict(product)
            product_json = json.dumps(product_dict)
            key = self._get_key(id_api)
            resp = await self.r.set(key, product_json)
            await self.r.expire(key, TTL_SECONDS)
            return bool(resp)

        except Exception as e:
            logging.info(f"Erro ao salvar produto {id_api} no Redis: {e}")
            return False
    
    async def create_or_update_all(self, products: List[ProductResponse]) -> bool:
        try:
            for product in products:
                await self.create_or_update(product.id_api, product)
                
            return True

        except Exception as e:
            logging.info(f"Erro ao salvar produtos no Redis: {e}")
            return False
    
    async def get(self, id_api: int) -> Optional[ProductResponse]:
        try:
            key = self._get_key(id_api)
            product_json = await self.r.get(key)
            if product_json:
                product_dict = json.loads(product_json)
                return mapper_dict_to_product(product_dict)
            return None

        except Exception:
            return None

    async def get_all(self) -> List[ProductResponse]:
        try:
            pattern = f"{self.keyspace}:*"
            keys = []
            async for key in self.r.scan_iter(match=pattern):
                keys.append(key)
            
            if not keys:
                return []
            
            # Buscar todos os valores de uma vez
            values = await self.r.mget(keys)
            
            products = []
            for value in values:
                if value:
                    try:
                        product_dict = json.loads(value)
                        products.append(mapper_dict_to_product(product_dict))
                    except Exception:
                        continue
            
            return products
            
        except Exception:
            return []
