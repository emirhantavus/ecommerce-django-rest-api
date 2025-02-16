from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING

MONGO_URI = "mongodb://localhost:27017"
DATABASE_NAME = "ecommerce_products_db"

client = AsyncIOMotorClient(MONGO_URI)
db = client[DATABASE_NAME]
products_collection = db["products"]

async def init_db():
      await products_collection.create_index(["name",ASCENDING],unique=True)