# download_thread.py
from PyQt6.QtCore import QThread, pyqtSignal
import requests, zipfile, os, io
from loguru import logger


class DownloadExtractThread(QThread):
    progressChanged = pyqtSignal(int)
    installSuccess = pyqtSignal(dict)
    installFailed = pyqtSignal(str)

    def __init__(self, plugin, plugin_dir):
        super().__init__()
        self.plugin = plugin
        self.plugin_dir = plugin_dir

    def run(self):
        try:
            name = self.plugin["name"]
            zip_url = self.plugin["zip_url"]

            # 当插件名为Base_Tools时，安装路径要变为根目录，此时传入的self.plugin_dir是plugins目录

            path = os.path.join(self.plugin_dir, name)

            logger.info("[插件下载器] 开始安装插件: {}".format(name))
            logger.info("[插件下载器] 插件下载地址: {}".format(zip_url))
            logger.info("[插件下载器] 插件安装路径: {}".format(path))

            # 下载
            resp = requests.get(zip_url, stream=True)
            total = int(resp.headers.get("content-length", 0))
            downloaded = 0
            buf = io.BytesIO()

            for chunk in resp.iter_content(1024):
                buf.write(chunk)
                downloaded += len(chunk)
                percent = int(downloaded * 100 / total)
                self.progressChanged.emit(percent)

            # 解压
            buf.seek(0)
            with zipfile.ZipFile(buf) as zf:
                zf.extractall(path)

            # # 如果安装的插件是Base_Tools，则更名为tool
            # if name == "Base_Tools":
            #     os.rename(path, os.path.join(self.plugin_dir, "tools"))

            self.installSuccess.emit(self.plugin)
        except Exception as e:
            self.installFailed.emit(str(e))
