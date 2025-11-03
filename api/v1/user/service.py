from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api.utils.exceptions import (
    exception_400_BAD_REQUEST,
    exception_401_UNAUTHORIZED,
    exception_404_NOT_FOUND,
)
from api.utils.security import get_password_hash, verify_password
from api.v1._shared.models import User
from api.v1._shared.schemas import (
    UserCreate,
    UserDelete,
    UserFilter,
    UserResponse,
    UserUpdate,
)
from api.v1.user.mapper import mapper_user_to_user_response


class UserService:

    def __init__(self, db: Session):
        self.db = db

    def list(
        self,
        skip: int = 0,
        limit: int = 10,
        user_filter: UserFilter = None
    ) -> List[UserResponse]:
        # Listagem com paginação, ordenação e filtros usando fastapi-filter
        query = select(User).where(User.flg_deleted == False)

        # Aplicar filtros usando fastapi-filter
        if user_filter:
            query = user_filter.filter(query)
            query = user_filter.sort(query)
        
        # Se não houver ordenação do filtro, aplicar padrão
        if user_filter is None or not user_filter.order_by:
            query = query.order_by(User.created_at.desc())

        # Aplicar paginação
        result = self.db.execute(query.offset(skip).limit(limit))
        users = result.scalars().all()

        # Converter para schema de resposta
        return [mapper_user_to_user_response(user) for user in users]


    def get(self, id: UUID) -> UserResponse:
        query = select(User).where(
            User.id == id,
            User.flg_deleted == False
        )
        result = self.db.execute(query)
        user = result.scalar_one_or_none()
        
        if not user:
            raise exception_404_NOT_FOUND(detail=f"Usuário com ID {id} não encontrado")
        
        return mapper_user_to_user_response(user)
    
    def user_exists(self, email: str) -> bool:
        query = select(User).where(
            User.email == email.lower()
        )
        result = self.db.execute(query)
        user = result.scalar_one_or_none()

        if user:
            return True
        
        return False
    
    
    def get_user_by_email(self, email: str, password: str) -> User:
        query = select(User).where(
            User.email == email,
            User.flg_deleted == False
        )
        result = self.db.execute(query)
        user = result.scalar_one_or_none()

        # Existe usuário? 
        if not self.user_exists(email):
            raise exception_404_NOT_FOUND(detail=f"Usuário com email {email} não encontrado")

        # Senha correta?
        if not verify_password(password, user.password):
            raise exception_401_UNAUTHORIZED(detail="Senha incorreta")
        
        # Retorna usuário
        return user

    def create(self, obj: UserCreate) -> UserResponse:
        # Verificar se email já existe
        query = select(User).where(
            User.email == obj.email,
            User.flg_deleted == False
        )
        result = self.db.execute(query)
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise exception_400_BAD_REQUEST(detail=f"Email {obj.email} já está em uso")
        
        # Hash da senha
        hashed_password = get_password_hash(obj.password)
        
        # Criar usuário
        new_user = User(
            name=obj.name,
            email=obj.email,
            password=hashed_password,
            permissions=obj.permissions or ['USER']
        )
        
        try:
            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)
        except IntegrityError as e:
            self.db.rollback()
            
            # Verificar se é erro de email duplicado
            if "email" in str(e.orig).lower() or "unique" in str(e.orig).lower():
                raise exception_400_BAD_REQUEST(detail=f"Email {obj.email} já está em uso")
            raise
        
        return mapper_user_to_user_response(new_user)

    def update(self, obj: UserUpdate) -> UserResponse:
        query = select(User).where(
            User.id == obj.id,
            User.flg_deleted == False
        )
        result = self.db.execute(query)
        user = result.scalar_one_or_none()
        
        if not user:
            raise exception_404_NOT_FOUND(detail=f"Usuário com ID {obj.id} não encontrado")
        
        # Atualizar campos se fornecidos usando model_dump (exclui None e id)
        update_data = obj.model_dump(exclude_none=True, exclude={"id", "password"})
        
        for field, value in update_data.items():
            setattr(user, field, value)
        
        # Password precisa de hash especial
        if obj.password is not None:
            user.password = get_password_hash(obj.password)
        
        self.db.commit()
        self.db.refresh(user)
        
        return mapper_user_to_user_response(user)

    def delete(self, obj: UserDelete) -> UserResponse:
        query = select(User).where(
            User.id == obj.id,
            User.flg_deleted == False
        )
        result = self.db.execute(query)
        user = result.scalar_one_or_none()
        
        if not verify_password(obj.password, user.password):
            raise exception_401_UNAUTHORIZED(detail="Senha incorreta")
        
        user.flg_deleted = True
        self.db.commit()
        
        return mapper_user_to_user_response(user)