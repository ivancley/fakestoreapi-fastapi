from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException

from api.v1._shared.schemas import (
    AccountCreate, 
    AccountLogin, 
    AccountResponse,
    TokenResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    UserCreate,
)
from api.v1.account.service import AccountService
from api.v1.account.mapper import mapper_account_create_to_user_create

class AccountUseCase:
    
    def __init__(self, db: Session):
        self.service = AccountService(db)
    
    async def register(self, data: AccountCreate) -> AccountResponse:
        user_create = mapper_account_create_to_user_create(data)
        return self.service.register(user_create)
    
    async def login(self, data: AccountLogin) -> TokenResponse:
        return self.service.login(data)
    
    async def refresh_token(self, data: RefreshTokenRequest) -> RefreshTokenResponse:
        return self.service.refresh_token(data.refresh_token)
    