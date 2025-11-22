from pydantic import Field, field_validator
from MongoModel import MongoModel
from bson.objectid import ObjectId
from typing import Optional


class ProjectModel(MongoModel):
    _id: Optional[ObjectId] = None
    project_id: str = Field(..., min_length=1)

    @field_validator("project_id")
    def validate_project_id(cls, value):
        if not value.isalnum():
            raise ValueError("project_id must be alphanumeric.")

        return value
