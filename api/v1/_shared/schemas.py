from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import BaseModel, Field, model_validator

from api.v1._shared.models import (
    BaseModel as CustomBaseModel,
    Favorite,
    Product,
    User,
    get_permissions,
)



class CustomBaseModel(BaseModel):
    #flg_deleted: bool = Field(False)
    model_config: Dict[str, Any] = {
        "arbitrary_types_allowed": True,
        "from_attributes": True 
    }


class UserBase(CustomBaseModel):
    name: str
    email: str


class UserCreate(BaseModel): 
    name: str 
    email: str 
    password: str
    permissions: Optional[List[str]] = Field(default=get_permissions()[0])


class UserUpdate(BaseModel):
    id: UUID
    name: Optional[str] = None
    password: Optional[str] = None
    permissions: Optional[List[str]] = None
    
    @model_validator(mode='after')
    def validate_permissoes(self):
        if self.permissions is not None:
            valid_perms = set(get_permissions())
            invalid = set(self.permissions) - valid_perms
            if invalid:
                raise ValueError(
                    f"Permissões inválidas: {', '.join(invalid)}. Permissões válidas: {', '.join(valid_perms)}"
                )
        return self


class UserResponse(BaseModel):
    id: UUID 
    name: str
    email: str
    permissions: List[str]
    created_at: datetime
    updated_at: datetime


class UserDelete(BaseModel):
    id: UUID
    password: str


class UserFilter(Filter):
    name__ilike: Optional[str] = None
    email__ilike: Optional[str] = None
    order_by: Optional[List[str]] = None
    search: Optional[str] = None

    class Constants(Filter.Constants):
        model = User
        search_model_fields = ["name", "email"]


class AccountCreate(BaseModel):
    name: str
    email: str
    password: str


class AccountLogin(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: str
    expires_in: int


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class RefreshTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_token: str


class AccountResponse(BaseModel):
    id: UUID
    name: str
    email: str
    permissions: List[str]
    created_at: datetime
    updated_at: datetime


class ProductBase(BaseModel):
    id: Optional[UUID] = None
    id_api: int
    title: str
    price: float
    description: str
    category: str
    image: str
    rate: float
    count: int


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    id: Optional[UUID] = None
    id_api: int
    title: Optional[str] = None
    price: Optional[float] = None
    description: Optional[str] = None
    category: Optional[str] = None
    image: Optional[str] = None
    rate: Optional[float] = None
    count: Optional[int] = None


class ProductResponse(ProductBase, CustomBaseModel):
    id: Optional[UUID] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ProductFilter(Filter):
    title__ilike: Optional[str] = None
    description__ilike: Optional[str] = None
    category__ilike: Optional[str] = None
    order_by: Optional[List[str]] = None
    search: Optional[str] = None

    class Constants(Filter.Constants):
        model = Product
        search_model_fields = ["title", "description", "category"]


class FavoriteBase(BaseModel):
    user_id: UUID
    product_id: UUID
    review: str


class FavoriteCreate(BaseModel):
    api_id: int
    review: Optional[str] = None


class FavoriteUpdate(BaseModel):
    id: UUID
    review: str = ""


class FavoriteResponse(BaseModel):
    id: UUID
    title: str
    image: str
    price: float
    review: Optional[str] = None


class FavoriteDelete(BaseModel):
    id: UUID


class FavoriteFilter(Filter):
    review__ilike: Optional[str] = None
    order_by: Optional[List[str]] = None
    search: Optional[str] = None

    class Constants(Filter.Constants):
        model = Favorite
        search_model_fields = ["review"]
