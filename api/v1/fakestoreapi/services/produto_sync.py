from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session  # Session síncrona

from api.utils.exceptions import exception_400_BAD_REQUEST, exception_404_NOT_FOUND
from api.v1._shared.models import Product
from api.v1._shared.schemas import (
    ProductCreate,
    ProductResponse,
    ProductUpdate,
)

class ProductServiceSync:
    """
    Versão síncrona do ProductService para o Celery
    """
    
    def __init__(self, db: Session):
        self.db = db

    def get_by_id_api(self, id_api: int):
        query = select(Product).where(
            Product.id_api == id_api,
            Product.flg_deleted == False
        )
        result = self.db.execute(query)
        return result.scalar_one_or_none()


    def save_or_update(self, product: ProductCreate) -> ProductResponse:
        product_exists = self.get_by_id_api(product.id_api)

        if product_exists:
            return self.update(product)
        else:
            return self.create(product)


    def create(self, product: ProductCreate) -> ProductResponse:
        new_product = Product(
            **product.model_dump(exclude_none=True)
        )
        
        try:
            self.db.add(new_product)
            self.db.commit()
            self.db.refresh(new_product)
        except IntegrityError as e:
            self.db.rollback()
            raise exception_400_BAD_REQUEST(detail=f"Erro ao criar produto: {str(e)}")
        
        return ProductResponse.model_validate(new_product)

    def update(self, product: ProductCreate) -> ProductResponse:
        product_exists = self.get_by_id_api(product.id_api)
        
        if not product_exists:
            raise exception_404_NOT_FOUND(detail=f"Produto com ID API {product.id_api} não encontrado")

        update_data = product.model_dump(exclude_none=True, exclude={"id_api"})
        
        for field, value in update_data.items():
            setattr(product_exists, field, value)
        
        try:
            self.db.commit()
            self.db.refresh(product_exists)
        except IntegrityError as e:
            self.db.rollback()
            raise exception_400_BAD_REQUEST(detail=f"Erro ao atualizar produto: {str(e)}")
        
        return ProductResponse.model_validate(product_exists)