import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from api.utils.db_services import AsyncSessionLocal
from api.v1._shared.models import User
from api.v1._shared.schemas import UserCreate
from sqlalchemy import select
from api.v1.user.service import UserService

async def create_inicial_user():
    db: AsyncSession = AsyncSessionLocal()
    user_service = UserService(db)  

    try:
        name = "Admin"
        email = "admin@gmail.com"
        password = "Senha@123"
        permissions = ["ADMIN"]

        query = select(User).where(
            User.email == email,
            User.flg_deleted == False
        )
        result = await db.execute(query)
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            print(f"\n\nUsuário com email {email} já existe\n\n")
            return
        

        user_create = UserCreate(name=name, email=email, password=password, permissions=permissions)
        await user_service.create(user_create)
        print(f"\n\nUsuário criado com sucesso\n\n")
        
    except Exception as e:
        print(f"\n\nErro ao criar usuário: {str(e)}\n\n")
        raise
    finally:
        await db.close()

if __name__ == "__main__":
    asyncio.run(create_inicial_user())