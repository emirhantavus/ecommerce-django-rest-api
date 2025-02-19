from fastapi import APIRouter , HTTPException , Depends
from typing import List , Dict
from app.models.product import Product
from app.core.database import products_collection
from bson import ObjectId
from app.dependency.dependencies import get_current_user

router = APIRouter()

@router.get("/", response_model=List[Product])
async def get_products():
      products = await products_collection.find().to_list()
      for product in products:
            product["id"] = str(product["_id"])
      return products

@router.post("/", response_model=Product)
async def create_product(product: Product, current_user: str = Depends(get_current_user)):
      product_dict = product.dict()
      product_dict["user_id"] = str(current_user)
      result = await products_collection.insert_one(product_dict)
      inserted_product = await products_collection.find_one({"_id":result.inserted_id})
      
      return {"message":"Product added successfuly.",
              "product_id":str(result.inserted_id),
              "name":inserted_product["name"],
              "price":inserted_product["price"],
              "user_id":str(inserted_product["user_id"])}

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