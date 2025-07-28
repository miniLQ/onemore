import os
import importlib.util
import json
from loguru import logger

# 根目录设置为项目根（你可以根据实际情况调整）
PLUGIN_DIR = os.path.join(os.path.dirname(__file__), ".")

def load_plugins(main_window):
    logger.info("Loading plugins")
    plugin_root = os.path.join(PLUGIN_DIR)
    if not os.path.exists(plugin_root):
        return

    for name in os.listdir(plugin_root):
        plugin_path = os.path.join(plugin_root, name)
        if not os.path.isdir(plugin_path):
            continue

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
                logger.info(f"[PluginLoader] Loaded plugin: {name}")
        except Exception as e:
            logger.error(f"[PluginLoader] Failed to load plugin {name}: {e}")
