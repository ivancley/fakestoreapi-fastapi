from api.v1._shared.schemas import ProductResponse
from typing import List, Dict, Any



def mapper_response_to_list_products(response: List[Dict[str, Any]]) -> List[ProductResponse]:
    result = []
    for product in response:
        result.append(mapper_response_to_product(product))
    return result


def mapper_response_to_product(response: Dict[str, Any]) -> ProductResponse:
    return ProductResponse(
        id_api=response['id'],
        title=response['title'],
        price=response['price'],
        description=response['description'],
        category=response['category'],
        image=response['image'],
        rate=response['rating']['rate'],
        count=response['rating']['count']
    )


def mapper_list_products_to_list_dict(products: List[ProductResponse]) -> List[Dict[str, Any]]:
    result = []
    for product in products:
        result.append(product.model_dump())
    return result


def mapper_dict_to_product(product_dict: Dict[str, Any]) -> ProductResponse:
    return ProductResponse(**product_dict)
    

def mapper_product_to_dict(product: ProductResponse) -> Dict[str, Any]:
    return product.model_dump()