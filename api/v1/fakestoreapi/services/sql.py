from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api.utils.exceptions import exception_400_BAD_REQUEST, exception_404_NOT_FOUND
from api.v1._shared.models import Product
from api.v1._shared.schemas import (
    ProductCreate,
    ProductResponse,
    ProductUpdate,
)

class ProductService:

    def __init__(self, db: Session):
        self.db = db

    def list(self) -> List[ProductResponse]:
        query = select(Product).where(Product.flg_deleted == False)
        
        result = self.db.execute(query)
        products = result.scalars().all()
        return [ProductResponse.model_validate(product) for product in products]

    def get(self, id: UUID) -> ProductResponse:
        query = select(Product).where(
            Product.id == id,
            Product.flg_deleted == False
        )
        result = self.db.execute(query)
        product = result.scalar_one_or_none()
        
        if not product:
            raise exception_404_NOT_FOUND(detail=f"Produto com ID {id} não encontrado")
        
        return ProductResponse.model_validate(product)
    
    def get_by_id_api(self, id_api: int):
        query = select(Product).where(
            Product.id_api == id_api,
            Product.flg_deleted == False
        )
        result = self.db.execute(query)
        return result.scalar_one_or_none()

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

    def update(self, product: ProductUpdate) -> ProductResponse:
        query = select(Product).where(
            Product.id == product.id,
            Product.flg_deleted == False
        )
        result = self.db.execute(query)
        product = result.scalar_one_or_none()
        
        if not product:
            raise exception_404_NOT_FOUND(detail=f"Produto com ID {product.id} não encontrado")
        
        update_data = product.model_dump(exclude_none=True, exclude={"id"})
        
        for field, value in update_data.items():
            setattr(product, field, value)
        
        self.db.commit()
        self.db.refresh(product)
        
        return ProductResponse.model_validate(product)

    def delete(self, id: int) -> ProductResponse:
        product = self.get(id)
        
        product.flg_deleted = True
        self.db.commit()
        
        return ProductResponse.model_validate(product)
    
    
    def save_or_update(self, product: ProductCreate) -> ProductResponse:
        product_exists = self.get_by_id_api(product.id_api)

        if product_exists:
            return self.update(product)
            
        else:
            return self.create(product)
       