# coding:utf-8
import os
import sys

from PyQt6.QtCore import Qt, QTranslator
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication
from qfluentwidgets import FluentTranslator

from app.common.config import cfg
from app.view.register_window import RegisterWindow


# 设置根目录
ROOTPATH = os.path.dirname(os.path.abspath(__file__))
sys.path.append(ROOTPATH)

# updater helper mode (run before UI)
if "--update-helper" in sys.argv:
    try:
        idx = sys.argv.index("--update-helper")
        update_file = sys.argv[idx + 1] if len(sys.argv) > idx + 1 else ""
        from app.common.app_updater import AppUpdater
        AppUpdater.run_update_helper(update_file)
    finally:
        sys.exit(0)

# 启动时清理更新残留文件
try:
    import shutil
    from pathlib import Path
    trash_dir = Path(ROOTPATH) / "_to_delete"
    if trash_dir.exists():
        shutil.rmtree(trash_dir, ignore_errors=True)
except:
    pass

# enable dpi scale
if cfg.get(cfg.dpiScale) != "Auto":
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
    os.environ["QT_SCALE_FACTOR"] = str(cfg.get(cfg.dpiScale))

# create application
app = QApplication(sys.argv)
app.setAttribute(Qt.ApplicationAttribute.AA_DontCreateNativeWidgetSiblings)

# internationalization
locale = cfg.get(cfg.language).value
translator = FluentTranslator(locale)
galleryTranslator = QTranslator()
galleryTranslator.load(locale, "app", ".", ":/app/i18n")

app.installTranslator(translator)
app.installTranslator(galleryTranslator)

# create main window
w = RegisterWindow()
w.show()

app.exec()
