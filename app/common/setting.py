# coding: utf-8
from pathlib import Path
from app.common.config import VERSION, YEAR, AUTHOR

# change DEBUG to False if you want to compile the code to exe
DEBUG = "__compiled__" not in globals()


YEAR = YEAR
AUTHOR = AUTHOR
VERSION = VERSION
APP_NAME = "OneMore"
HELP_URL = "https://github.com/miniLQ/onemore/issues"
REPO_URL = "https://github.com/miniLQ/onemore"
FEEDBACK_URL = "https://github.com/miniLQ/onemore/issues"
DOC_URL = "https://www.iliuqi.com/archives/onemore-tool-detail"
RELEASE_API_URL = "https://api.github.com/repos/miniLQ/onemore/releases/latest"

CONFIG_FOLDER = Path('AppData').absolute()
CONFIG_FILE = CONFIG_FOLDER / "config.json"
