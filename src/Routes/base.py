from fastapi import APIRouter, Depends
from helper.config import get_config, Config

base_router = APIRouter(
    prefix="/api/v1",
    tags=["api_v1"],
)


@base_router.get("/")
async def health_check(app_config:Config = Depends(get_config)):
    app_config = get_config()
    app_name = app_config.APP_NAME

    app_version = app_config.APP_VERSION
    return {
        "status": "ok",
        "app_name": app_name,
        "app_version": app_version,
    }
