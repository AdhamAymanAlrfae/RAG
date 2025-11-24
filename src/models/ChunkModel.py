from .BaseDataModel import BaseDataModel
from schemas.db import DataChunkSchema
from schemas.Enums import DataBaseEnum
from pymongo import InsertOne
from motor.motor_asyncio import AsyncIOMotorCollection
from bson.objectid import ObjectId


class ChunkModel(BaseDataModel):
    collection: AsyncIOMotorCollection

    def __init__(self, db_client):
        super().__init__(db_client)
        self.collection = db_client[DataBaseEnum.COLLECTION_CHUNK_NAME.value]

    async def insert_chunk(self, chunk: DataChunkSchema):
        result = await self.collection.insert_one(chunk.model_dump(by_alias=True, exclude_none=True))
        chunk._id = result.inserted_id
        return chunk

    async def get_chunk(self, project_id: str):
        record = await self.collection.find_one({
            "project_id": ObjectId(project_id)
        })

        return None if (record == None) else DataChunkSchema(**record)

    async def insert_many_chunks(self, chunks: list[DataChunkSchema], batch_size: int = 100):

        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i+batch_size]

            requests = [
                InsertOne(chunk.model_dump(by_alias=True, exclude_none=True)) for chunk in batch
            ]

            await self.collection.bulk_write(requests)

            return len(chunks)

    async def delete_chunks_by_project_id(self, project_id: ObjectId):
        result = await self.collection.delete_many({
            "chunk_project_id": project_id
        })

        return result.deleted_count
