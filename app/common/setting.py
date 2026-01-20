# coding: utf-8
from pathlib import Path

# change DEBUG to False if you want to compile the code to exe
DEBUG = "__compiled__" not in globals()


YEAR = 2024
AUTHOR = "iliuqi"
VERSION = "v2.0.5"
APP_NAME = "OneMore"
HELP_URL = "https://github.com/miniLQ/onemore/issues"
REPO_URL = "https://github.com/miniLQ/onemore"
FEEDBACK_URL = "https://github.com/miniLQ/onemore/issues"
DOC_URL = "https://qfluentwidgets.com/"

CONFIG_FOLDER = Path('AppData').absolute()
CONFIG_FILE = CONFIG_FOLDER / "config.json"
