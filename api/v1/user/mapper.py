from api.v1._shared.models import User
from api.v1._shared.schemas import UserResponse

def mapper_user_to_user_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        permissions=user.permissions or ['USER'],
        created_at=user.created_at,
        updated_at=user.updated_at
    )