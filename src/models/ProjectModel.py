from .BaseDataModel import BaseDataModel
from schemas.Enums import DataBaseEnum
from schemas.db import ProjectSchema
from motor.motor_asyncio import AsyncIOMotorCollection
from bson.objectid import ObjectId


class ProjectModel(BaseDataModel):

    collection: AsyncIOMotorCollection

    def __init__(self, db_client):
        super().__init__(db_client)
        self.collection = self.db_client[
            DataBaseEnum.COLLECTION_PROJECT_NAME.value]

    async def create_project(self, project: ProjectSchema):
        result = await self.collection.insert_one(project.model_dump())
        project._id = result.inserted_id
        return project

    async def get_project_or_create_one(self, project_id: str):
        result = await self.collection.find_one({
            "project_id": project_id
        })
        if result is None:
            project = ProjectSchema(project_id=project_id)
            project = await self.create_project(project=project)
            return project

        return ProjectSchema(**result)

    async def get_all_projects(self, page: int = 1, page_size: int = 10):

        total_documents = self.collection.count_documents({})

        total_pages = total_documents // page_size

        if total_documents % page_size > 0:
            total_pages += 1

        curser = self.collection.find({}).skip(
            (page-1)*page_size).limit(page_size)

        projects = []

        async for document in curser:
            projects.append(ProjectSchema(**document))

        return projects, total_pages
