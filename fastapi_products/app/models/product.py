from pydantic import BaseModel , field_validator , Field
from typing import Optional
from datetime import datetime

class Product(BaseModel):
      id: Optional[str] = None
      name: str
      description: Optional[str] = None
      price: float
      created_at: datetime=Field(default_factory=datetime.utcnow)
      user_id: Optional[str] = None
      
      
@field_validator("created_at")
def serialize_created_at(cls, value: datetime) -> str:
      return value.strftime("%d-%m-%Y %H:%M") #sonra bak. date formatını ayarla.