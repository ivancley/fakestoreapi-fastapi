from api.v1._shared.models import Favorite
from api.v1._shared.schemas import FavoriteResponse

def mapper_favorite_to_favorite_response(favorite: Favorite) -> FavoriteResponse:
    return FavoriteResponse(
        id=favorite.id,
        title=favorite.product.title,
        image=favorite.product.image,
        price=favorite.product.price,
        review=favorite.review
    )