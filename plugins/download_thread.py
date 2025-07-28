# download_thread.py
from PyQt6.QtCore import QThread, pyqtSignal
import requests, zipfile, os, io


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
            path = os.path.join(self.plugin_dir, name)

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

            self.installSuccess.emit(self.plugin)
        except Exception as e:
            self.installFailed.emit(str(e))
