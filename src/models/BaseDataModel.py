from helper.config import get_config
from motor.motor_asyncio import AsyncIOMotorDatabase


class BaseDataModel:
    def __init__(self, db_client: AsyncIOMotorDatabase):
        self.db_client = db_client
        self.app_config = get_config()
