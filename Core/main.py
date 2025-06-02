from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from fastapi.openapi.utils import get_openapi
from app.routers import (
    products, wishlist, profile, categories,
    addresses, payments, admin  # ⬅️ افزودن admin router
)

app = FastAPI(title="Core Service")

# Register all routers including admin
for router in (
    products, wishlist, profile,
    categories, addresses, payments, admin
):
    app.include_router(router.router)

# Auth schema for FastAPI docs
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://localhost:8000/user/iam/login")

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
        "UserOAuth2": {
            "type": "oauth2",
            "flows": {
                "password": {
                    "tokenUrl": "http://localhost:8000/user/iam/login",
                    "scopes": {"user": "User access"}
                }
            }
        },
        "AdminOAuth2": {
            "type": "oauth2",
            "flows": {
                "password": {
                    "tokenUrl": "http://localhost:8000/admin/iam/login",
                    "scopes": {"admin": "Admin access"}
                }
            }
        }
    }
    for path in openapi_schema["paths"].values():
        for method in path.values():
            tags = method.get("tags", [])
            if "Admin" in tags:
                method["security"] = [{"AdminOAuth2": ["admin"]}]
            else:
                method["security"] = [{"UserOAuth2": ["user"]}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# from fastapi import FastAPI
# from app.routers import products, wishlist, profile, categories, addresses, payments

# app = FastAPI(title="Core Service")

# for router in (products, wishlist, profile, categories, addresses, payments):
#     app.include_router(router.router)

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
#         "OAuth2PasswordBearer": {
#             "type": "oauth2",
#             "flows": {
#                 "password": {
#                     "tokenUrl": "http://localhost:8000/user/iam/login",
#                     "scopes": {}
#                 }
#             }
#         }
#     }
#     for path in openapi_schema["paths"].values():
#         for method in path.values():
#             method["security"] = [{"OAuth2PasswordBearer": []}]
#     app.openapi_schema = openapi_schema
#     return app.openapi_schema

# app.openapi = custom_openapi

