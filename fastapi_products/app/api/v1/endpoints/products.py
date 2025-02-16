from fastapi import APIRouter , HTTPException
from typing import List , Dict
from app.models.product import Product
from app.core.database import products_collection
from bson import ObjectId

router = APIRouter()

@router.get("/", response_model=List[Product])
async def get_products():
      products = await products_collection.find().to_list()
      for product in products:
            product["id"] = str(product["_id"])
      return products

@router.post("/", response_model=Product)
async def create_product(product: Product):
      product_dict = product.dict()
      result = await products_collection.insert_one(product_dict)
      product_dict["id"] = str(result.inserted_id)
      return product_dict

@router.get("/{product_id}",response_model=Product)
async def get_products_by_id(product_id: str):
      product = await products_collection.find_one({"_id":ObjectId(product_id)})
      if not product:
            raise HTTPException(status_code=404, detail="Product not found")
      product["id"] = str(product["_id"])
      return product

@router.delete("/{product_id}", response_model=Dict[str, str])
async def delete_product(product_id: str):
      if not ObjectId.is_valid(product_id):
            raise HTTPException(status_code=400, detail="Invalid product ID format")

      result = await products_collection.delete_one({"_id": ObjectId(product_id)})

      if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Product not found")

      return {"message": f"Product with id {product_id} has been deleted."}