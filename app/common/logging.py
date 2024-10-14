from loguru import logger
from .config import ROOTPATH
import os
import time

APPDATA = os.path.join(ROOTPATH, "appData")

log_file_path = os.path.join(APPDATA, "log", "{}.txt".format(time.strftime("%Y-%m-%d")))
os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

logger.add(log_file_path, rotation="00:00", retention="7 days", level="DEBUG")