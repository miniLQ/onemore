# coding: utf-8
from PyQt6.QtCore import QObject, pyqtSignal
import requests
import os
from loguru import logger
from app.common.config import ROOTPATH

from qfluentwidgets import (
    SearchLineEdit, BodyLabel, SubtitleLabel,
    InfoBar, InfoBarPosition, FluentIcon as FIF, FluentIconBase
)

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
        logger.info("正在检查插件索引文件更新...")
        logger.info("正在从 https://raw.githubusercontent.com/miniLQ/onemore/refs/heads/dev/plugins/plugin_index.json 下载插件索引文件")
        resp = requests.get(
            "https://raw.githubusercontent.com/miniLQ/onemore/refs/heads/dev/plugins/plugin_index.json")
        if resp.status_code == 200:
            with open(os.path.join(ROOTPATH, "plugins", "plugin_index.json"), "w", encoding="utf-8") as f:
                f.write(resp.text)
            logger.info("插件索引文件已更新")
        else:
            logger.error(f"插件索引文件更新失败，状态码: {resp.status_code}")

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