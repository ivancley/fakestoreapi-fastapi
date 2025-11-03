from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1._shared.schemas import (
    AccountCreate, 
    AccountLogin, 
    AccountResponse,
    TokenResponse,
    RefreshTokenRequest,
    RefreshTokenResponse
)
from api.v1.account.service import AccountService
from api.v1.account.mapper import mapper_account_create_to_user_create, mapper_user_to_account_response
from api.v1._shared.models import User

class AccountUseCase:
    
    def __init__(self, db: AsyncSession):
        self.service = AccountService(db)
    
    async def register(self, data: AccountCreate) -> AccountResponse:
        user_create = mapper_account_create_to_user_create(data)
        return await self.service.register(user_create)
    
    async def login(self, data: AccountLogin) -> TokenResponse:
        return await self.service.login(data)
    
    async def refresh_token(self, data: RefreshTokenRequest) -> RefreshTokenResponse:
        return await self.service.refresh_token(data.refresh_token)
    
    async def get_me(self, current_user: User) -> AccountResponse:
        return mapper_user_to_account_response(current_user)