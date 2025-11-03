from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from api.utils.exceptions import exception_400_BAD_REQUEST, exception_404_NOT_FOUND
from api.v1._shared.models import Product
from api.v1._shared.schemas import (
    ProductCreate,
    ProductResponse,
    ProductUpdate,
)

class ProductService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list(self) -> List[ProductResponse]:
        query = select(Product).where(Product.flg_deleted == False)
        
        result = await self.db.execute(query)
        products = result.scalars().all()
        return [ProductResponse.model_validate(product) for product in products]


    async def get(self, id: UUID) -> ProductResponse:
        query = select(Product).where(
            Product.id == id,
            Product.flg_deleted == False
        )
        result = await self.db.execute(query)
        product = result.scalar_one_or_none()
        
        if not product:
            raise exception_404_NOT_FOUND(detail=f"Produto com ID {id} não encontrado")
        
        return ProductResponse.model_validate(product)
    

    async def get_by_id_api(self, id_api: int):
        query = select(Product).where(
            Product.id_api == id_api,
            Product.flg_deleted == False
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()


    async def create(self, product: ProductCreate) -> ProductResponse:
        new_product = Product(
            **product.model_dump(exclude_none=True)
        )
        
        try:
            self.db.add(new_product)
            await self.db.commit()
            await self.db.refresh(new_product)

        except IntegrityError as e:
            await self.db.rollback()
            raise exception_400_BAD_REQUEST(detail=f"Erro ao criar produto: {str(e)}")
        
        return ProductResponse.model_validate(new_product)


    async def update(self, product: ProductUpdate) -> ProductResponse:
        query = select(Product).where(
            Product.id == product.id,
            Product.flg_deleted == False
        )
        result = await self.db.execute(query)
        product = result.scalar_one_or_none()
        
        if not product:
            raise exception_404_NOT_FOUND(detail=f"Produto com ID {product.id} não encontrado")
        
        update_data = product.model_dump(exclude_none=True, exclude={"id"})
        
        for field, value in update_data.items():
            setattr(product, field, value)
        
        await self.db.commit()
        await self.db.refresh(product)
        
        return ProductResponse.model_validate(product)


    async def delete(self, id: int) -> ProductResponse:
        product = await self.get(id)
        
        product.flg_deleted = True
        await self.db.commit()
        
        return ProductResponse.model_validate(product)
    
    
    async def save_or_update(self, product: ProductCreate) -> ProductResponse:
        product_exists = await self.get_by_id_api(product.id_api)

        if product_exists:
            return await self.update(product)
            
        else:
            return await self.create(product)
       