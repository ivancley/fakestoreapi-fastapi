from datetime import datetime
from enum import Enum as PyEnum
import logging
from typing import List
import uuid

import pytz
from sqlalchemy import (
    ARRAY,
    Boolean,
    Column,
    DateTime, 
    String,
    Float,
    Integer,
    Text,
    ForeignKey
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import  declarative_base, relationship


Base = declarative_base()
tz = pytz.timezone('America/Sao_Paulo')
logger = logging.getLogger(__name__)


class PermissionType(str, PyEnum):
    USER = "USER"
    ADMIN = "ADMIN"

def get_permissions() -> List[str]:
    return [PermissionType.ADMIN.value, PermissionType.USER.value]


class BaseModel(Base):
    __abstract__ = True
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(tz), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(tz), onupdate=lambda: datetime.now(tz), nullable=False)
    flg_deleted = Column(Boolean, default=False, nullable=False, server_default='false')


class User(BaseModel):
    __tablename__ = 'user'
       
    name = Column(String(255), nullable=False)   
    email = Column(String(255), nullable=False, unique=True, index=True)   
    password = Column(String(255), nullable=True)
    permissions = Column(ARRAY(String), nullable=False, default=list, server_default='{}')

    favorites = relationship('Favorite', back_populates='user')

class Product(BaseModel):
    __tablename__ = 'product' 
    
    id_api = Column(Integer, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(255), nullable=False)
    image = Column(String(255), nullable=False)
    rate = Column(Float, nullable=False)
    count = Column(Integer, nullable=False)

    favorites = relationship('Favorite', back_populates='product')


class Favorite(BaseModel):
    __tablename__ = 'favorite'
    
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey('user.id'), nullable=False)
    product_id = Column(PG_UUID(as_uuid=True), ForeignKey('product.id'), nullable=False)
    review = Column(Text, nullable=False)
    
    user = relationship('User', back_populates='favorites', lazy='selectin')
    product = relationship('Product', back_populates='favorites', lazy='selectin')