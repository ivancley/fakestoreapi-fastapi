from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, Path, Query
from fastapi_filter import FilterDepends
from sqlalchemy.orm import Session

from api.utils.db_services import get_db
from api.utils.security import get_current_user
from api.v1._shared.models import User
from api.v1._shared.schemas import FavoriteResponse, FavoriteFilter, FavoriteUpdate, FavoriteDelete, FavoriteCreate
from api.v1.favorite.use_case import FavoriteUseCase


router = APIRouter(
    prefix="/favorites",
    tags=["Favorites"], 
)


@router.get("", response_model=List[FavoriteResponse])
async def list(
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(10, ge=1, le=100, description="Número máximo de registros a retornar"),
    favorite_filter: FavoriteFilter = FilterDepends(FavoriteFilter),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[FavoriteResponse]:
    """
    Listar favoritos do usuário logado com filtros, ordenação e busca
    
    - skip: Número de registros para pular, o padrão é 0
    - limit: Número máximo de registros a retornar (padrão: 10, máximo: 100)
    - Filtros disponíveis via query params:
        - review__ilike: Busca parcial na review (case-insensitive)
        - search: Busca textual nos campos review
        - order_by: Ordenação (ex: order_by=review ou order_by=-created_at)
    """
    use_case = FavoriteUseCase(db)
    return await use_case.list(
        skip=skip,
        limit=limit,
        favorite_filter=favorite_filter,
        current_user=current_user,
    )


@router.get("/{id}", response_model=FavoriteResponse)
async def get_by_id(
    id: UUID = Path(..., description="ID do favorito"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> FavoriteResponse:  
    """
    Busca um favorito pelo ID
    
    - id: ID do favorito
    """
    use_case = FavoriteUseCase(db)
    return await use_case.get(id, current_user)


@router.post("", response_model=FavoriteResponse)
async def create(
    favorite: FavoriteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> FavoriteResponse:
    """
    Cria um favorito

    - api_id: ID do produto na API externa
    - review: Review do favorito (opcional)
    """
    use_case = FavoriteUseCase(db)
    return await use_case.create(favorite, current_user)

@router.put("", response_model=FavoriteResponse)
async def update(
    Favorite: FavoriteUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> FavoriteResponse:
    """
    Atualiza um favorito
    
    - review: novo review do favorito
    """
    use_case = FavoriteUseCase(db)
    return await use_case.update(Favorite, current_user)


@router.delete("/{id}", response_model=FavoriteResponse)
async def delete(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> FavoriteResponse:
    """
    Deleta um favorito
    
    - id: ID do favorito a ser deletado
    """
    use_case = FavoriteUseCase(db)
    return await use_case.delete(id, current_user)