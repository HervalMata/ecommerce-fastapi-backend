#from typing import Optional

#from pydantic import BaseModel, ConfigDict

from app.schemas.schema_base import SchemaBaseModel

# class CategoryCreateBase(BaseModel):
#     name: str
#     description: Optional[str] = None
#
# class CategoryUpdate(BaseModel):
#     id: int
#     name: Optional[str] = None
#     description: Optional[str] = None
#
# class CategoryRead(BaseModel):
#     id: int
#     name: str
#     description: Optional[str] = None
#
#     model_config = ConfigDict(
#         from_attributes=True,
#         exclude_none=True
#     )

class CategorySchema(SchemaBaseModel):
    id: int
    name: str
    description: str | None = None
    