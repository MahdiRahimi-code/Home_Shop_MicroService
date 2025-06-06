# app/main.py
from fastapi import FastAPI
from app.routers import (
    products, wishlist, profile, categories, addresses, payments,
    admin, discounts, reviews, basket, wallet, receipts, ratings
)

app = FastAPI(title="Core Service")

for router in (
    products, wishlist, profile, categories, addresses, payments,
    admin, discounts, reviews, basket, wallet, receipts, ratings
):
    app.include_router(router.router)

# --- تنظیم OpenAPI برای هم کاربران و هم ادمین ---
from fastapi.security import OAuth2PasswordBearer
from fastapi.openapi.utils import get_openapi

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://localhost:8000/user/iam/login")
oauth2_scheme_admin = OAuth2PasswordBearer(tokenUrl="http://localhost:8000/admin/iam/login")

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Core Service",
        version="1.0.0",
        description="API for core service",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2User": {
            "type": "oauth2",
            "flows": {"password": {"tokenUrl": "http://localhost:8000/user/iam/login", "scopes": {}}}
        },
        "OAuth2Admin": {
            "type": "oauth2",
            "flows": {"password": {"tokenUrl": "http://localhost:8000/admin/iam/login", "scopes": {}}}
        }
    }
    # تعیین Security برای هر روت
    for path, path_item in openapi_schema["paths"].items():
        for method, op in path_item.items():
            # اگر مسیر با "/admin" شروع شود، از OAuth2Admin استفاده کند
            if path.startswith("/admin"):
                op["security"] = [{"OAuth2Admin": []}]
            else:
                op["security"] = [{"OAuth2User": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi









# # app/main.py
# from fastapi import FastAPI
# from app.routers import products, wishlist, profile, categories, addresses, payments, admin

# app = FastAPI(title="Core Service")

# # به ترتیبِ دلخواه، همهٔ روترها را اضافه می‌کنیم:
# for router in (products, wishlist, profile, categories, addresses, payments, admin):
#     app.include_router(router.router)

# # ------------- تنظیمِ OpenAPI برای Authorization -------------
# from fastapi.security import OAuth2PasswordBearer
# from fastapi.openapi.utils import get_openapi

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://localhost:8000/user/iam/login")

# def custom_openapi():
#     if app.openapi_schema:
#         return app.openapi_schema
#     openapi_schema = get_openapi(
#         title="Core Service",
#         version="1.0.0",
#         description="API for core service",
#         routes=app.routes,
#     )
#     openapi_schema["components"]["securitySchemes"] = {
#         # برای User
#         "OAuth2PasswordBearer": {
#             "type": "oauth2",
#             "flows": {
#                 "password": {
#                     "tokenUrl": "http://localhost:8000/user/iam/login",
#                     "scopes": {}
#                 }
#             }
#         },
#         # برای Admin
#         "OAuth2PasswordBearerAdmin": {
#             "type": "oauth2",
#             "flows": {
#                 "password": {
#                     "tokenUrl": "http://localhost:8000/admin/iam/login",
#                     "scopes": {}
#                 }
#             }
#         }
#     }
#     # به همهٔ pathها، قطعه‌های امنیت را اضافه می‌کنیم:
#     for path in openapi_schema["paths"].values():
#         for method in path.values():
#             # اگر path به /admin/... تعلق دارد، از روشِ Admin استفاده کن
#             if any(p.startswith("/admin") for p in method.get("operationId", "").split()):
#                 method["security"] = [{"OAuth2PasswordBearerAdmin": []}]
#             else:
#                 method["security"] = [{"OAuth2PasswordBearer": []}]
#     app.openapi_schema = openapi_schema
#     return app.openapi_schema

# app.openapi = custom_openapi


#----------------------------------------------


# from fastapi import FastAPI
# from fastapi.security import OAuth2PasswordBearer
# from fastapi.openapi.utils import get_openapi
# from app.routers import (
#     products, wishlist, profile, categories,
#     addresses, payments, admin  # ⬅️ افزودن admin router
# )

# app = FastAPI(title="Core Service")

# # Register all routers including admin
# for router in (
#     products, wishlist, profile,
#     categories, addresses, payments, admin
# ):
#     app.include_router(router.router)

# # Auth schema for FastAPI docs
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://localhost:8000/user/iam/login")

# def custom_openapi():
#     if app.openapi_schema:
#         return app.openapi_schema
#     openapi_schema = get_openapi(
#         title="Core Service",
#         version="1.0.0",
#         description="API for core service",
#         routes=app.routes,
#     )
#     openapi_schema["components"]["securitySchemes"] = {
#         "UserOAuth2": {
#             "type": "oauth2",
#             "flows": {
#                 "password": {
#                     "tokenUrl": "http://localhost:8000/user/iam/login",
#                     "scopes": {"user": "User access"}
#                 }
#             }
#         },
#         "AdminOAuth2": {
#             "type": "oauth2",
#             "flows": {
#                 "password": {
#                     "tokenUrl": "http://localhost:8000/admin/iam/login",
#                     "scopes": {"admin": "Admin access"}
#                 }
#             }
#         }
#     }
#     for path in openapi_schema["paths"].values():
#         for method in path.values():
#             tags = method.get("tags", [])
#             if "Admin" in tags:
#                 method["security"] = [{"AdminOAuth2": ["admin"]}]
#             else:
#                 method["security"] = [{"UserOAuth2": ["user"]}]
#     app.openapi_schema = openapi_schema
#     return app.openapi_schema


# app.openapi = custom_openapi
