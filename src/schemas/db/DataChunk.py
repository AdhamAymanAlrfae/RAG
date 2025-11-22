from .MongoModel import MongoModel
from pydantic import Field
from typing import Optional
from bson.objectid import ObjectId


class DataChunkModel(MongoModel):
    _id: Optional[ObjectId] = None
    chunk_text: str = Field(..., min_length=1)
    chunk_metadata: dict
    chunk_order: int = Field(..., ge=0)
    chunk_project_id: ObjectId
