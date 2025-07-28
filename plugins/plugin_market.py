import os
import json
import time

import requests
import zipfile
import io

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QHBoxLayout, QLabel, QPushButton, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QIcon
from qfluentwidgets import (
    SearchLineEdit, BodyLabel, SubtitleLabel,
    InfoBar, InfoBarPosition, FluentIcon as FIF, FluentIconBase
)

from loguru import logger
from app.common.config import ROOTPATH
from plugins.download_thread import DownloadExtractThread

CURRENT_DIR = os.path.dirname(__file__)

class PluginMarket(QWidget):
    def __init__(self, plugin_dir: str, parent=None):
        super().__init__(parent)
        self.setObjectName("plugin-market")
        self.plugin_dir = plugin_dir
        self.all_plugins = []
        self.plugin_rows = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 20, 32, 20)
        layout.setSpacing(12)

        layout.addWidget(SubtitleLabel("🛒 插件市场", self))

        # 增加一行提示，提示内容为：安装插件后，必须重启软件才能生效！
        layout.addWidget(BodyLabel("在这里你可以浏览和安装各种插件，提升软件功能！", self))
        self.search_bar = SearchLineEdit(self)
        self.search_bar.setPlaceholderText("搜索插件...")
        self.search_bar.textChanged.connect(self.filter_plugins)
        layout.addWidget(self.search_bar)

        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)

        self.scrollContent = QWidget()
        self.scrollLayout = QVBoxLayout(self.scrollContent)
        self.scrollLayout.setSpacing(6)
        self.scrollLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.scrollArea.setWidget(self.scrollContent)
        layout.addWidget(self.scrollArea)

        self.load_plugins()

    def load_plugins(self):
        index_path = os.path.join(self.plugin_dir, "plugin_index.json")
        if not os.path.exists(index_path):
            InfoBar.error(
                parent=self,
                title="错误",
                content="未找到 plugin_index.json",
                position=InfoBarPosition.TOP
            )
            return

        with open(index_path, "r", encoding="utf-8") as f:
            self.all_plugins = json.load(f)

        for plugin in self.all_plugins:
            self.add_plugin_row(plugin)

    def add_plugin_row(self, plugin: dict):
        name = plugin.get("name", "未知插件")
        desc = plugin.get("description", "")
        version = plugin.get("version", "未知")
        author = plugin.get("author", "匿名")

        plugin_path = os.path.join(self.plugin_dir, name)
        logo_path = os.path.join(CURRENT_DIR, plugin.get("logo", ""))
        if logo_path == "":
            logo_path = os.path.join(ROOTPATH, "app", "resource", "images", "logo.png")
        is_installed = os.path.exists(plugin_path)

        # row frame
        row = QFrame(self.scrollContent)
        row.setStyleSheet("QFrame { background-color: #f4f4f4; border-radius: 8px; }")
        row.setFixedHeight(70)

        layout = QHBoxLayout(row)
        layout.setContentsMargins(12, 6, 12, 6)

        # icon
        icon_label = QLabel()
        icon_pix = QPixmap(logo_path).scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio)
        icon_label.setPixmap(icon_pix)
        layout.addWidget(icon_label)

        # name & description
        text_container = QVBoxLayout()
        name_label = QLabel(f"<b>{name}</b>")
        desc_label = BodyLabel(f"{desc}\n作者：{author}，版本：{version}）")
        text_container.addWidget(name_label)
        text_container.addWidget(desc_label)
        layout.addLayout(text_container)

        layout.addStretch()

        # button
        button = QPushButton("卸载" if is_installed else "安装")
        button.setFixedWidth(80)
        layout.addWidget(button)

        if is_installed:
            button.clicked.connect(lambda _, p=name, b=button, r=row: self.uninstall_plugin(p, b, r))
        else:
            button.clicked.connect(lambda _, p=plugin, b=button: self.install_plugin(p, b))

        self.scrollLayout.addWidget(row)
        self.plugin_rows.append((plugin, row))

    def filter_plugins(self, text):
        text = text.lower().strip()
        for plugin, row in self.plugin_rows:
            name = plugin.get("name", "").lower()
            desc = plugin.get("description", "").lower()
            row.setVisible(text in name or text in desc)

    def uninstall_plugin(self, name, button, row):
        try:
            import shutil
            shutil.rmtree(os.path.join(self.plugin_dir, name))
            InfoBar.success(
                parent=self,
                title="成功",
                content=f"插件『{name}』已卸载，请重启软件以生效",
                position=InfoBarPosition.TOP,
                duration=10000,
                isClosable=True
            )
            button.setText("安装")
            button.clicked.disconnect()
            button.clicked.connect(lambda _, p=self._get_plugin_by_name(name), b=button: self.install_plugin(p, b))
        except Exception as e:
            InfoBar.error(
                parent=self,
                title="卸载失败",
                content=str(e),
                position=InfoBarPosition.TOP,
                duration=10000,
                isClosable=True
            )

    def install_plugin(self, plugin, button):
        name = plugin.get("name", "unknown")
        zip_url = plugin.get("zip_url", "")

        button.setEnabled(False)

        try:
            if zip_url:
                thread = DownloadExtractThread(plugin, self.plugin_dir)
                thread.progressChanged.connect(lambda p: button.setText(f"{p}%"))
                thread.installSuccess.connect(lambda p: self._on_install_success(p, button))
                thread.installFailed.connect(lambda err: self._on_install_failed(err, button))
                thread.start()

                self._thread = thread  # 防止线程被GC回收

            else:
                os.makedirs(os.path.join(self.plugin_dir, name), exist_ok=True)
                with open(os.path.join(self.plugin_dir, name, "metadata.json"), "w", encoding="utf-8") as f:
                    json.dump(plugin, f, indent=2)
                with open(os.path.join(self.plugin_dir, name, "plugin.py"), "w", encoding="utf-8") as f:
                    f.write("# TODO: implement register(main_window)\n")

            # button.clicked.disconnect()
            # button.clicked.connect(lambda _, p=name, b=button, r=None: self.uninstall_plugin(p, b, r))
        except Exception as e:
            InfoBar.error(
                parent=self,
                title="安装失败",
                content=str(e),
                position=InfoBarPosition.TOP
            )

    def _get_plugin_by_name(self, name):
        for p in self.all_plugins:
            if p.get("name") == name:
                return p
        return None

    def _on_install_success(self, plugin, button):
        InfoBar.success(
            parent=self,
            title="安装成功",
            content=f"插件『{plugin['name']}』安装成功，请重启软件以生效",
            position=InfoBarPosition.TOP,
            duration=10000,
            isClosable=True
        )
        button.setText("卸载")
        button.setEnabled(True)
        button.clicked.disconnect()
        button.clicked.connect(lambda _, p=plugin['name'], b=button, r=None: self.uninstall_plugin(p, b, r))

    def _on_install_failed(self, error, button):
        InfoBar.error(
            parent=self,
            title="安装失败",
            content=error,
            position=InfoBarPosition.TOP,
            duration=10000,
            isClosable=True
        )
        button.setText("安装")
        button.setEnabled(True)