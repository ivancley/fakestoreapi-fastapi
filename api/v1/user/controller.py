from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, Path, Query
from fastapi_filter import FilterDepends
from sqlalchemy.orm import Session

from api.utils.db_services import get_db
from api.utils.security import get_current_user
from api.v1._shared.models import User
from api.v1._shared.schemas import UserDelete, UserResponse, UserUpdate, UserFilter
from api.v1.user.use_case import UserUseCase


router = APIRouter(
    prefix="/users",
    tags=["Users"], 
)


@router.get("", response_model=List[UserResponse])
async def list(
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(10, ge=1, le=100, description="Número máximo de registros a retornar"),
    user_filter: UserFilter = FilterDepends(UserFilter),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[UserResponse]:
    """
    Listar usuários com filtros, ordenação e busca
    
    - skip: Número de registros para pular, o padrão é 0
    - limit: Número máximo de registros a retornar (padrão: 10, máximo: 100)
    - Filtros disponíveis via query params:
        - name__ilike: Busca parcial no nome (case-insensitive)
        - email__ilike: Busca parcial no email (case-insensitive)
        - search: Busca textual nos campos name e email
        - order_by: Ordenação (ex: order_by=name ou order_by=-created_at)
    """
    use_case = UserUseCase(db)
    return await use_case.list(
        skip=skip,
        limit=limit,
        user_filter=user_filter
    )


@router.get("/{id}", response_model=UserResponse)
async def get_by_id(
    id: UUID = Path(..., description="ID do usuário"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Busca um usuário pelo ID
    
    - id: ID do usuário
    """
    use_case = UserUseCase(db)
    return await use_case.get(id)

@router.put("", response_model=UserResponse)
async def update(
    User: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Atualiza um usuário
    
    - User: Dados do usuário a ser atualizado
    """
    use_case = UserUseCase(db)
    return await use_case.update(User, current_user)


@router.delete("", response_model=UserResponse)
async def delete(
    User: UserDelete,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Deleta um usuário validando senha
    
    - User: Dados do usuário a ser deletado
    """
    use_case = UserUseCase(db)
    return await use_case.delete(User)