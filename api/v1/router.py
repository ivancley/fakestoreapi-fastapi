from fastapi import APIRouter
from api.v1.user.controller import router as user_router
from api.v1.account.controller import router as account_router
from api.v1.fakestoreapi.controller import router as fakestoreapi_router
from api.v1.favorite.controller import router as favorite_router

routes = APIRouter(prefix="/api/v1")

routes.include_router(account_router)
routes.include_router(user_router)
routes.include_router(fakestoreapi_router)
routes.include_router(favorite_router)