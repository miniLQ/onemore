# coding:utf-8
import sys
from enum import Enum
import os
from PyQt6.QtCore import QLocale
from qfluentwidgets import (qconfig, QConfig, ConfigItem, OptionsConfigItem, BoolValidator,
                            OptionsValidator, Theme, FolderValidator, ConfigSerializer)

from .setting import CONFIG_FILE

class Language(Enum):
    """ Language enumeration """

    CHINESE_SIMPLIFIED = QLocale(QLocale.Language.Chinese, QLocale.Country.China)
    CHINESE_TRADITIONAL = QLocale(QLocale.Language.Chinese, QLocale.Country.HongKong)
    ENGLISH = QLocale(QLocale.Language.English)
    AUTO = QLocale()


class LanguageSerializer(ConfigSerializer):
    """ Language serializer """

    def serialize(self, language):
        return language.value.name() if language != Language.AUTO else "Auto"

    def deserialize(self, value: str):
        return Language(QLocale(value)) if value != "Auto" else Language.AUTO


def isWin11():
    return sys.platform == 'win32' and sys.getwindowsversion().build >= 22000

currentPath = os.path.dirname(os.path.abspath(__file__))
# rootpath为currentpath的上两级目录
ROOTPATH = os.path.dirname(os.path.dirname(currentPath))

class Config(QConfig):
    """ Config of application """

    # TODO: ADD YOUR CONFIG GROUP HERE

    # register
    rememberMe = ConfigItem("Register", "RememberMe", True)
    email = ConfigItem("Register", "Email", "")
    password = ConfigItem("Register", "password", "")

    # main window
    micaEnabled = ConfigItem("MainWindow", "MicaEnabled", isWin11(), BoolValidator())
    dpiScale = OptionsConfigItem(
        "MainWindow", "DpiScale", "Auto", OptionsValidator([1, 1.25, 1.5, 1.75, 2, "Auto"]), restart=True)
    language = OptionsConfigItem(
        "MainWindow", "Language", QLocale.Language.Chinese, OptionsValidator(Language), LanguageSerializer(), restart=True)

    # software update
    checkUpdateAtStartUp = ConfigItem("Update", "CheckUpdateAtStartUp", True, BoolValidator())

    rootPath = ConfigItem("RootPath", "RootPath", ROOTPATH, FolderValidator())

YEAR = 2024
AUTHOR = "iliuqi"
VERSION = "0.1.7"
HELP_URL = "https://qfluentwidgets.com"
REPO_URL = "https://github.com/zhiyiYo/PyQt-Fluent-Widgets"
EXAMPLE_URL = "https://github.com/zhiyiYo/PyQt-Fluent-Widgets/tree/PyQt6/examples"
FEEDBACK_URL = "https://github.com/zhiyiYo/PyQt-Fluent-Widgets/issues"
RELEASE_URL = "https://github.com/zhiyiYo/PyQt-Fluent-Widgets/releases/latest"
ZH_SUPPORT_URL = "https://qfluentwidgets.com/zh/price/"
EN_SUPPORT_URL = "https://qfluentwidgets.com/price/"



cfg = Config()
cfg.themeMode.value = Theme.AUTO
qconfig.load(str(CONFIG_FILE.absolute()), cfg)