import asyncio
import logging
from typing import Any, Dict, List

from api.utils.celery import celery_app
from api.utils.db_services import SyncSessionLocal 
from api.utils.exceptions import exception_500_INTERNAL_SERVER_ERROR
from api.v1._shared.schemas import ProductCreate
from api.v1.fakestoreapi.mapper import mapper_list_products_to_list_dict
from api.v1.fakestoreapi.services.api import APIService
from api.v1.fakestoreapi.services.redis import RedisService
from api.v1.fakestoreapi.services.produto_sync import ProductServiceSync

DELAY_TIME = 60
MAX_RETRIES = 3


@celery_app.task(
    name="get_products_api",
    bind=True,
    max_retries=MAX_RETRIES,
    default_retry_delay=DELAY_TIME  
)
def get_products_api(self):
    # O Celery não suporta async/await diretamente, então criei um loop
    logging.info(f"Celery starting get_products_api")
    loop = None
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        serviceAPI = APIService()
        serviceRedis = RedisService()
        products = loop.run_until_complete(serviceAPI.list())
        
        if products:
            # O Celery não aceita objetos, então converti para dicionário
            products_dict = mapper_list_products_to_list_dict(products)
            save_or_update_products_in_database_sql_task.delay(products_dict)
            loop.run_until_complete(serviceRedis.create_or_update_all(products))
        
    except Exception as e:
        logging.error(f"Erro ao buscar produtos da API: {e}")
        self.retry(exc=e)

    finally:
        if loop:
            loop.close()



@celery_app.task(
    name="update_products_task",
    bind=True,
    max_retries=MAX_RETRIES,
    default_retry_delay=DELAY_TIME  
)
def save_or_update_products_in_database_sql_task(self, products: List[Dict[str, Any]]):
    logging.info(f"Celery starting save_or_update_products_in_database_sql_task")
    db = SyncSessionLocal()
    serviceSQL = ProductServiceSync(db)
    try:
        for product in products:
            serviceSQL.save_or_update(ProductCreate(**product))
        
    except Exception as e:
        self.retry(exc=e)

    finally:
        db.close()


@celery_app.task(
    name="update_product_task",
    max_retries=MAX_RETRIES,
    default_retry_delay=DELAY_TIME  
)
def save_or_update_product_task(product: Dict[str, Any]):
    logging.info(f"Celery starting save_or_update_product_task")
    db = SyncSessionLocal()
    serviceSQL = ProductServiceSync(db)
    try:
        serviceSQL.save_or_update(ProductCreate(**product))

    except Exception as e:
        logging.error(f"Erro ao salvar produto: {e}")
        raise exception_500_INTERNAL_SERVER_ERROR(detail=f"Erro ao buscar produto: {str(e)}")

    finally:
        db.close()
