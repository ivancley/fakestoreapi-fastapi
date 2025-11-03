from typing import List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from api.v1._shared.schemas import (
    UserDelete,
    UserFilter,
    UserResponse,
    UserUpdate,
)
from api.v1.user.service import UserService
from api.v1._shared.models import User
from api.utils.exceptions import exception_403_FORBIDDEN

class UserUseCase:

    def __init__(self, db: AsyncSession):
        self.service = UserService(db)

    async def list(
        self,
        skip: int = 0,
        limit: int = 10,
        user_filter: UserFilter = None
    ) -> List[UserResponse]:
        return await self.service.list(
            skip=skip,
            limit=limit,
            user_filter=user_filter
        )

    async def get(self, id: UUID) -> UserResponse:
        return await self.service.get(id)

    async def update(self, user: UserUpdate, current_user: User) -> UserResponse:
        # Se estiverm adicionando a permissão de Admin, verificar se o usuário logado é admin
        if "ADMIN" in user.permissions: 
            if "ADMIN" in current_user.permissions:
                return await self.service.update(user)
            else:
                raise exception_403_FORBIDDEN(detail="Você não tem permissão para alterar o tipo do usuário")

        return await self.service.update(user)

    async def delete(self, user: UserDelete) -> UserResponse:
        return await self.service.delete(user)