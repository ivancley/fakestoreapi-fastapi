from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.utils.db_services import get_db
from api.utils.security import get_current_user
from api.v1._shared.models import User
from api.v1._shared.schemas import ProductResponse
from api.v1.fakestoreapi.use_case import ProductUseCase

router = APIRouter(
    prefix="/fakestoreapi",
    tags=["FakeStoreAPI"], 
)


@router.get("", response_model=List[ProductResponse])
async def list(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[ProductResponse]:
    use_case = ProductUseCase(db)
    return await use_case.list()

@router.get("/{id}", response_model=ProductResponse)
async def get(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProductResponse:
    use_case = ProductUseCase(db)
    return await use_case.get(id)