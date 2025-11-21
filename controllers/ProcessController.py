from .BaseController import BaseController
from .ProjectController import ProjectController
from schemas.Enums import ProcessingEnum
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_core.documents import Document
import os


class ProcessController(BaseController):

    def __init__(self, project_id: str):
        super().__init__()

        self.project_id = project_id
        self.project_dir = ProjectController().get_project_path(project_id=self.project_id)

    def get_file_extension(self, file_name: str):
        return os.path.splitext(file_name)[-1]

    def get_file_loader(self, file_name: str):
        ext = self.get_file_extension(file_name=file_name)
        file_path = os.path.join(self.project_dir, file_name)
        if ext == ProcessingEnum.TEXT.value:
            return TextLoader(file_path=file_path, encoding="utf-8")

        if ext == ProcessingEnum.PDF.value:
            return PyPDFLoader(file_path=file_path)

    def get_file_content(self, file_name: str):
        loader = self.get_file_loader(file_name=file_name)
        return loader.load()

    def process_file_content(self, file_content: list[Document], chunk_size: int = 100, overlap_size: int = 20):
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=overlap_size)

        file_content_texts = [doc.page_content for doc in file_content]

        file_content_metadata = [doc.metadata for doc in file_content]

        chunks = splitter.create_documents(
            texts=file_content_texts, metadatas=file_content_metadata)

        return chunks
