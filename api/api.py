from ninja import NinjaAPI
from .routers.categories import category_router
from .routers.products import product_router


api = NinjaAPI()

api.add_router("/categories", category_router)
api.add_router("/products", product_router)