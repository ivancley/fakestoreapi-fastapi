from api.v1._shared.models import User
from api.v1._shared.schemas import UserResponse

def mapper_user_to_user_response(self, user: User) -> UserResponse:
    return UserResponse.model_validate({
        **user.__dict__,
        "permissions": user.permissions or []
    })