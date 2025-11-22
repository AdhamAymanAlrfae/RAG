from fastapi import FastAPI
from Routes import base, data
from motor.motor_asyncio import AsyncIOMotorClient
from helper.config import get_config
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    config = get_config()
    app.client = AsyncIOMotorClient(config.MONGODB_URL)
    app.db = app.client[config.MONGODB_DATABASE]

    yield

    # Shutdown
    app.client.close()

app = FastAPI(lifespan=lifespan)


app.include_router(base.base_router)
app.include_router(data.data_router)
