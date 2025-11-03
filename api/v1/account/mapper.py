from api.v1._shared.schemas import AccountCreate, UserCreate

def mapper_account_create_to_user_create(account: AccountCreate) -> UserCreate:
    return UserCreate(
        name=account.name,
        email=account.email.lower(),
        password=account.password,
        permissions=["USER"]
    )