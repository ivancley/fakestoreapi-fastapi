from typing import List

import requests

from api.utils.exceptions import exception_500_INTERNAL_SERVER_ERROR
from api.v1._shared.schemas import ProductResponse
from api.v1.fakestoreapi.mapper import (
    mapper_response_to_list_products,
    mapper_response_to_product,
)

URL = 'https://fakestoreapi.com/products'


class APIService:

    async def list(self) -> List[ProductResponse]:
        try:
            response = requests.get(URL)
            return mapper_response_to_list_products(response.json())

        except Exception as e:
            raise exception_500_INTERNAL_SERVER_ERROR(
                detail=f"Erro ao listar produtos: {str(e)}"
            )

    async def get(self, id: int) -> ProductResponse:
        try:
            response = requests.get(f"{URL}/{id}")
            product_data = response.json()
            return mapper_response_to_product(product_data)
        except Exception as e:
            raise exception_500_INTERNAL_SERVER_ERROR(
                detail=f"Erro ao buscar produto: {str(e)}"
            )