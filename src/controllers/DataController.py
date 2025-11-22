from .BaseController import BaseController
from fastapi import UploadFile
from schemas.Enums import ResponseSignal
from uuid import uuid4
import os
import re


class DataController(BaseController):
    def __init__(self):
        super().__init__()

    def validate_uploaded_file(self, file: UploadFile):
        if file.content_type not in self.config.FILE_TYPES:
            return False, ResponseSignal.FILE_TYPE_NOT_SUPPORTED.value
        if file.size > self.config.FILE_MAX_SIZE * 1024 * 1024:
            return False, ResponseSignal.FILE_SIZE_EXCEEDED.value
        return True, ResponseSignal.FILE_VALIDATED_SUCCESS.value

    def get_clean_name(self, orig_file_name: str):
        name, ext = os.path.splitext(orig_file_name)
        name = re.sub(r'[^\w]', '', name)
        ext = ext.lower().replace(".", "")
        cleaned_file_name = f"{name}.{ext}"

        return cleaned_file_name

    def generate_unique_name(self, orig_file_name):
        clean_name = self.get_clean_name(orig_file_name)
        unique_name = f"{uuid4().hex}_{clean_name}"
        return unique_name
