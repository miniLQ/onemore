# coding: utf-8
from PyQt6.QtCore import QObject, pyqtSignal
import requests
import os,io
from loguru import logger
from app.common.config import ROOTPATH
import zipfile

from qfluentwidgets import (
    SearchLineEdit, BodyLabel, SubtitleLabel,
    InfoBar, InfoBarPosition, FluentIcon as FIF, FluentIconBase
)

PLUGIN_DIR = os.path.join(ROOTPATH, 'plugins')

class SignalBus(QObject):
    """ Signal bus """
    # 定义一个信号，当checkUpdate被调用时会触发
    # 这个信号可以在其他地方连接到槽函数
    checkUpdateSig = pyqtSignal()
    micaEnableChanged = pyqtSignal(bool)

    def __init__(self):
        super().__init__()

        # 连接信号到槽函数
        self.checkUpdateSig.connect(self.Update)

    # 如果checkUpdateSig信号被触发，则会调用checkUpdate方法
    def Update(self, auto=False):
        """ Check for updates """
        # 从这个地址下载https://raw.githubusercontent.com/miniLQ/onemore/refs/heads/dev/plugins/plugin_index.json
        # logger.info("正在检查插件索引文件更新...")
        # logger.info("正在从 https://raw.githubusercontent.com/miniLQ/onemore/refs/heads/master/plugins/plugin_index.json 下载文件")
        # if not os.path.exists(PLUGIN_DIR):
        #     os.makedirs(PLUGIN_DIR)
        # try:
        #     # 下载插件索引文件, 设置超时时间2s，如果2s内无法下载索引文件，则抛出异常
        #     resp = requests.get(
        #         url="https://raw.githubusercontent.com/miniLQ/onemore/refs/heads/master/plugins/plugin_index.json",
        #         timeout=2
        #     )
        #     if resp.status_code == 200:
        #         with open(os.path.join(ROOTPATH, "plugins", "plugin_index.json"), "w", encoding="utf-8") as f:
        #             f.write(resp.text)
        #         logger.info("[插件管理器] 索引文件已更新")
        #     else:
        #         logger.error(f"[插件管理器] 索引文件更新失败，状态码: {resp.status_code}")
        # except Exception as e:
        #     logger.error(e)
        #
        # logger.info("正在从https://raw.githubusercontent.com/miniLQ/onemore/refs/heads/master/plugins/download_thread.py 下载文件")
        # try:
        #     # 下载插件索引文件, 设置超时时间2s，如果2s内无法下载索引文件，则抛出异常
        #     resp = requests.get(
        #         url="https://raw.githubusercontent.com/miniLQ/onemore/refs/heads/master/plugins/download_thread.py",
        #         timeout=2
        #     )
        #     if resp.status_code == 200:
        #         with open(os.path.join(ROOTPATH, "plugins", "download_thread.py"), "w", encoding="utf-8") as f:
        #             f.write(resp.text)
        #         logger.info("[插件管理器] 下载模块已更新")
        #     else:
        #         logger.error(f"[插件管理器] 下载模块更新失败，状态码: {resp.status_code}")
        # except Exception as e:
        #     logger.error(e)
        # logger.info("正在从https://raw.githubusercontent.com/miniLQ/onemore/refs/heads/master/plugins/plugin_loader.py 下载文件")
        # try:
        #     # 下载插件索引文件, 设置超时时间2s，如果2s内无法下载索引文件，则抛出异常
        #     resp = requests.get(
        #         url="https://raw.githubusercontent.com/miniLQ/onemore/refs/heads/master/plugins/plugin_loader.py",
        #         timeout=2
        #     )
        #     if resp.status_code == 200:
        #         with open(os.path.join(ROOTPATH, "plugins", "plugin_loader.py"), "w", encoding="utf-8") as f:
        #             f.write(resp.text)
        #         logger.info("[插件管理器] 加载模块已更新")
        #     else:
        #         logger.error(f"[插件管理器] 加载模块更新失败，状态码: {resp.status_code}")
        # except Exception as e:
        #     logger.error(e)
        # logger.info("正在从https://raw.githubusercontent.com/miniLQ/onemore/refs/heads/master/plugins/plugin_market.py 下载文件")
        # try:
        #     # 下载插件文件, 设置超时时间2s，如果2s内无法下载文件，则抛出异常
        #     resp = requests.get(
        #         url="https://raw.githubusercontent.com/miniLQ/onemore/refs/heads/master/plugins/plugin_market.py",
        #         timeout=2
        #     )
        #     if resp.status_code == 200:
        #         with open(os.path.join(ROOTPATH, "plugins", "plugin_market.py"), "w", encoding="utf-8") as f:
        #             f.write(resp.text)
        #         logger.info("[插件管理器] 插件市场模块已更新")
        #     else:
        #         logger.error(f"[插件管理器] 插件市场模块更新失败，状态码: {resp.status_code}")
        # except Exception as e:
        #     logger.error(e)

        logger.info("[插件管理器] 正在更新插件管理器...")
        # 从这个地址下载https://raw.githubusercontent.com/miniLQ/onemore/refs/heads/dev/plugins/plugin_index.json
        logger.info("正在从 https://raw.githubusercontent.com/miniLQ/onemore/refs/heads/master/release/plugins.zip 下载文件")
        if not os.path.exists(PLUGIN_DIR):
            os.makedirs(PLUGIN_DIR)
        try:
            resp = requests.get("https://raw.githubusercontent.com/miniLQ/onemore/refs/heads/master/release/plugins.zip", stream=True)
            buf = io.BytesIO()

            for chunk in resp.iter_content(1024):
                buf.write(chunk)
            logger.success("[插件管理器] 插件市场模块已下载")
            # 解压
            buf.seek(0)
            with zipfile.ZipFile(buf) as zf:
                zf.extractall(PLUGIN_DIR)
            logger.success("[插件管理器] 插件市场模块已解压")
        except Exception as e:
            logger.error(e)

        if auto == False:
            InfoBar.success(
                parent=None,
                title="更新成功",
                content=f"插件市场已更新，请重启软件以生效",
                position=InfoBarPosition.TOP,
                duration=10000,
                isClosable=False
            )


signalBus = SignalBus()