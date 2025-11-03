from api.v1._shared.schemas import AccountCreate, UserCreate, AccountResponse
from api.v1._shared.models import User

def mapper_account_create_to_user_create(account: AccountCreate) -> UserCreate:
    return UserCreate(
        name=account.name,
        email=account.email.lower(),
        password=account.password,
        permissions=["USER"]
    )

def mapper_user_to_account_response(user: User) -> AccountResponse:
    return AccountResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        permissions=user.permissions or ['USER'],
        created_at=user.created_at,
        updated_at=user.updated_at
    )