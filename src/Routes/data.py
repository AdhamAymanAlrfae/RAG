from fastapi import UploadFile, APIRouter, Depends, status, Request
from fastapi.responses import JSONResponse
from helper.config import get_config, Config
from controllers import DataController, ProjectController, ProcessController
from schemas import ProcessRequest
from schemas.Enums import ResponseSignal
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from schemas.db.DataChunkSchema import DataChunkSchema
import aiofiles
import logging
import os

logger = logging.getLogger("uvicorn.error")

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["data"])


@data_router.post("/upload/{project_id}")
async def upload_file(request: Request, project_id: str, file: UploadFile, app_config: Config = Depends(get_config)):

    project_model = ProjectModel(
        db_client=request.app.db
    )
    project = await project_model.get_project_or_create_one(project_id=project_id)
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
            "file_id": unique_file_name,
            "project_id": str(project._id)
        })


@data_router.post("/process/{project_id}")
async def process_endpoint(request: Request, project_id: str, process_request: ProcessRequest):
    file_id = process_request.file_id
    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    do_reset = process_request.do_reset

    process_controller = ProcessController(project_id=project_id)

    project_model = ProjectModel(
        db_client=request.app.db
    )

    project = await project_model.get_project_or_create_one(
        project_id=project_id
    )
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

    file_chunk_record = [
        DataChunkSchema(
            chunk_text=chunk.page_content,
            chunk_metadata=chunk.metadata,
            chunk_order=i,
            chunk_project_id=project.id
        )
        for i, chunk in enumerate(chunks)
    ]

    chunk_model = ChunkModel(
        db_client=request.app.db
    )

    if do_reset:
        _ = await chunk_model.delete_chunks_by_project_id(project_id=project.id)

    no_records = await chunk_model.insert_many_chunks(
        chunks=file_chunk_record,
    )

    return JSONResponse(
        content={
            "signal": ResponseSignal.PROCESSING_SUCCESS.value,
            "inserted_chunks": no_records
        }
    )
