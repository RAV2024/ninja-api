from ninja import NinjaAPI

from .routers.categories import category_router
from .routers.products import product_router
from .routers.auth import auth_router
from .routers.users import user_router
from .routers.wishlist import wishlist_router
from .routers.orders import order_router
from .routers.admin import admin_router



api = NinjaAPI()

api.add_router("/auth/", auth_router)
api.add_router("/admin/", admin_router)
api.add_router("/user/", user_router)
api.add_router("/categories", category_router)
api.add_router("/products", product_router)
api.add_router("/wishlist", wishlist_router)
api.add_router("/orders", order_router)


