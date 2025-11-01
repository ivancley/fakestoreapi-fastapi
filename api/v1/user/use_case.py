from typing import List
from uuid import UUID

from sqlalchemy.orm import Session

from api.v1._shared.schemas import (
    UserDelete,
    UserFilter,
    UserResponse,
    UserUpdate,
)
from api.v1.user.service import UserService

class UserUseCase:

    def __init__(self, db: Session):
        self.service = UserService(db)

    def list(
        self,
        skip: int = 0,
        limit: int = 10,
        user_filter: UserFilter = None
    ) -> List[UserResponse]:
        return self.service.list(
            skip=skip,
            limit=limit,
            user_filter=user_filter
        )

    def get(self, id: UUID) -> UserResponse:
        return self.service.get(id)

    def update(self, obj: UserUpdate) -> UserResponse:
        return self.service.update(obj)

    def delete(self, obj: UserDelete) -> UserResponse:
        return self.service.delete(obj)