from helper.config import get_config, Config
import os


class BaseController:
    def __init__(self):
        self.config: Config = get_config()

        self.root_path = os.path.dirname(os.path.dirname(__file__))
        self.files_dir = os.path.join(self.root_path, "assets", "files")
