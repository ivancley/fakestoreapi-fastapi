from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.utils.db_services import get_db
from api.utils.exceptions import (
    exception_500_INTERNAL_SERVER_ERROR,
)
from api.utils.security import get_current_user
from api.v1._shared.models import User
from api.v1._shared.schemas import (
    AccountCreate,
    AccountLogin,
    AccountResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    TokenResponse,
)
from api.v1.account.use_case import AccountUseCase

router = APIRouter(
    prefix="/account",
    tags=["Account"], 
)


@router.post(
    "/register",
    response_model=AccountResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nova conta"
)
async def register(
    data: AccountCreate, 
    db: AsyncSession = Depends(get_db)
):
    """
    Registrar novo usuário
    
    - name: Nome completo do usuário
    - email: Email único do usuário
    - password: Senha para acesso
    """
    use_case = AccountUseCase(db)
    account = await use_case.register(data)
    return account
   

@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Fazer login"
)
async def login(
    data: AccountLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    Autenticar usuário e retornar tokens de acesso e refresh.
    
    - email: Email do usuário
    - password: Senha do usuário
    """
    try:
        use_case = AccountUseCase(db)
        token_response = await use_case.login(data=data)
        return token_response
    
    except Exception as e:
        raise exception_500_INTERNAL_SERVER_ERROR(
            f"Erro interno ao fazer login: {str(e)}"
        )


@router.post(
    "/refresh",
    response_model=RefreshTokenResponse,
    summary="Renovar token de acesso"
)
async def refresh_token(
    data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Gerar novo token de acesso usando refresh token.
    
    - refresh_token: Refresh token válido obtido no login (deve ser enviado no body)
    """
    try:
        use_case = AccountUseCase(db)
        refresh_response = await use_case.refresh_token(data=data)
        return refresh_response
    
    except Exception as e:
        raise exception_500_INTERNAL_SERVER_ERROR(
            f"Erro interno ao renovar token: {str(e)}"
        )


@router.get(
    "/me",
    response_model=AccountResponse,
    summary="Obter perfil do usuário autenticado"
)
async def get_me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obter perfil do usuário autenticado.
    """
    try:
        use_case = AccountUseCase(db)
        return await use_case.get_me(current_user)
    
    except Exception as e:
        raise exception_500_INTERNAL_SERVER_ERROR(
            f"Erro interno ao obter perfil: {str(e)}"
        )

