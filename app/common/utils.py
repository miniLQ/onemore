import uuid
import os

def generate_uuid():
    return (str(uuid.uuid4()).replace('-', ''))[:7]

def linuxPath2winPath(path):
    return os.path.normpath(path).replace(os.sep, os.path.normcase(os.sep))

import subprocess

def is_python_installed():
    try:
        # 尝试运行 `python --version`
        subprocess.run(["python", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except FileNotFoundError:
        # 未找到 `python` 命令
        return False
    except subprocess.CalledProcessError:
        # 找到 `python` 命令，但执行失败（可能是其他原因）
        return True