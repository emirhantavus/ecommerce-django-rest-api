from fastapi import FastAPI
from app.api.v1.endpoints.products import router as products_router

app = FastAPI(title="Products Service")

app.include_router(products_router, prefix="/products", tags=["products"])