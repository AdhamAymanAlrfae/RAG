from fastapi import UploadFile, APIRouter, Depends, status
from fastapi.responses import JSONResponse
from helper.config import get_config, Config
from controllers import DataController, ProjectController, ProcessController
from schemas import ProcessRequest
from schemas.Enums import ResponseSignal
import aiofiles
import os
import logging

logger = logging.getLogger("uvicorn.error")

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["data"])


@data_router.post("/upload/{project_id}")
async def upload_file(project_id: str, file: UploadFile, app_config: Config = Depends(get_config)):
    data_controller = DataController()
    is_valid, signal = data_controller.validate_uploaded_file(file=file)
    if not is_valid:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message": signal})

    project_dir_path = ProjectController().get_project_path(project_id)
    unique_file_name = data_controller.generate_unique_name(file.filename)

    file_path = os.path.join(project_dir_path, unique_file_name)

    try:
        async with aiofiles.open(file_path, "wb") as f:
            while chunk := await file.read(app_config.FILE_DEFAULT_CHUNK_SIZE):
                await f.write(chunk)
    except Exception as e:
        logger.error(f"Error while upload the file: {e}")

        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message": ResponseSignal.FILE_UPLOAD_FAILED.value})

    return JSONResponse(
        content={
            "message": ResponseSignal.FILE_UPLOAD_SUCCESS.value,
            "file_id": unique_file_name})


@data_router.post("/process/{project_id}")
async def process_endpoint(project_id: str, request: ProcessRequest):
    file_id = request.file_id
    chunk_size = request.chunk_size
    overlap_size = request.overlap_size

    process_controller = ProcessController(project_id=project_id)

    try:
        content = process_controller.get_file_content(file_id)
    except Exception as e:
        logger.error(f"File failed upload {e}")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "signal": ResponseSignal.FILE_UPLOAD_FAILED.value
        })

    chunks = process_controller.process_file_content(
        file_content=content, chunk_size=chunk_size, overlap_size=overlap_size)

    if chunks is None or len(chunks) == 0:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "signal": ResponseSignal.PROCESSING_FAILED.value
        })
    return chunks
