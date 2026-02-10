import os
import importlib.util
import json
from loguru import logger
import sys


BASE_DIR = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else os.path.dirname(__file__))
PLUGIN_DIR = os.path.join(BASE_DIR, "plugins")

#logger.info(PLUGIN_DIR)

def load_plugins(main_window):
    #logger.info("Loading plugins")
    plugin_root = os.path.join(PLUGIN_DIR)
    if not os.path.exists(plugin_root):
        return

    for name in os.listdir(plugin_root):
        plugin_path = os.path.join(plugin_root, name)
        # 跳过插件资源目录
        if "plugin_resources" in plugin_path:
            continue
        if not os.path.isdir(plugin_path):
            continue

        # 检查是否存在__init__.py 文件，如果不存在新建空文件
        init_path = os.path.join(plugin_path, "__init__.py")
        if not os.path.exists(init_path):
            with open(init_path, "w", encoding="utf-8") as f:
                f.write("# This is an empty __init__.py file for plugin {}".format(name))

        entry_path = os.path.join(plugin_path, "plugin.py")
        if not os.path.exists(entry_path):
            continue

        # 动态加载 plugin.py
        spec = importlib.util.spec_from_file_location(f"{name}_plugin", entry_path)
        if not spec or not spec.loader:
            continue
        module = importlib.util.module_from_spec(spec)

        try:
            spec.loader.exec_module(module)
            if hasattr(module, "register"):
                module.register(main_window)
                logger.info(f"[插件管理器] 加载插件: {name}")
        except Exception as e:
            logger.error(f"[插件管理器] 加载插件失败 {name}: {e}")