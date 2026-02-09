import os
import sysconfig
from pathlib import Path
from shutil import copy, copytree

# https://blog.csdn.net/qq_25262697/article/details/129302819
# https://www.cnblogs.com/happylee666/articles/16158458.html
args = [
    'nuitka',
    '--standalone',
    '--assume-yes-for-downloads',
    '--mingw64',
    '--windows-icon-from-ico=./app/resource/images/logo.ico',
    '--enable-plugins=pyqt6',
    '--show-memory',
    '--show-progress',
    '--windows-console-mode=force',
    '--output-dir=./build',
    # '--nofollow-import-to=plugins',
    '--include-package=yaml',
    '--include-data-dir=app/resource=app/resource',
    #'--include-data-dir=plugins=plugins',
    './main.py'
]

os.system(' '.join(args))

# copy site-packages to dist folder
dist_folder = Path("build/main.dist")
site_packages = Path(sysconfig.get_paths()["purelib"])

copied_libs = []

for src in copied_libs:
    src = site_packages / src
    dist = dist_folder / src.name

    print(f"Coping site-packages `{src}` to `{dist}`")

    try:
        if src.is_file():
            copy(src, dist)
        else:
            copytree(src, dist)
    except:
        pass


# copy standard library
copied_files = ["ctypes", "hashlib.py", "hmac.py", "random.py", "secrets.py", "uuid.py"]
for file in copied_files:
    src = site_packages.parent / file
    dist = dist_folder / src.name

    print(f"Coping stand library `{src}` to `{dist}`")

    try:
        if src.is_file():
            copy(src, dist)
        else:
            copytree(src, dist)
    except:
        pass
