from .BaseSchema import BaseSchema
from pydantic import Field
from typing import Optional
from bson.objectid import ObjectId


class DataChunkSchema(BaseSchema):
    id: Optional[ObjectId] = Field(None, alias="_id")
    chunk_text: str = Field(..., min_length=1)
    chunk_metadata: dict
    chunk_order: int = Field(..., ge=0)
    chunk_project_id: ObjectId
