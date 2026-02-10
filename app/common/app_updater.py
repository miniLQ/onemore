# coding: utf-8
"""
应用程序自动更新模块
支持从 GitHub Releases 下载并安装更新
"""
import os
import sys
import subprocess
import time
import tempfile
import zipfile
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, Callable

import requests
from PyQt6.QtCore import QThread, pyqtSignal
from loguru import logger

from .config import ROOTPATH
from .setting import VERSION, REPO_URL


def _is_packaged() -> bool:
    """判断是否为打包后的可执行环境（兼容 Nuitka/PyInstaller）"""
    if getattr(sys, 'frozen', False):
        return True
    if globals().get('__compiled__', False):
        return True
    if getattr(sys, '_MEIPASS', None) is not None:
        return True
    exe_name = Path(sys.executable).name.lower()
    if exe_name.endswith('.exe') and not exe_name.startswith('python'):
        return True
    return False


class UpdateChecker(QThread):
    """检查更新的线程"""
    
    # 信号：(有更新, 最新版本, 下载URL, 更新日志)
    checkFinished = pyqtSignal(bool, str, str, str)
    checkError = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.repo_owner = "miniLQ"
        self.repo_name = "onemore"
        
    def run(self):
        """检查 GitHub Releases 获取最新版本"""
        try:
            api_url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/releases/latest"
            logger.info(f"正在检查更新: {api_url}")
            
            response = requests.get(api_url, timeout=10)
            if response.status_code != 200:
                self.checkError.emit(f"检查更新失败: HTTP {response.status_code}")
                return
            
            data = response.json()
            #logger.info(data)
            latest_version = data.get("tag_name", "")
            release_notes = data.get("body", "无更新说明")
            
            # 查找 Windows 可执行文件或 zip 包
            download_url = None
            for asset in data.get("assets", []):
                name = asset.get("name", "").lower()
                if name.endswith(".zip") or name.endswith(".exe"):
                    download_url = asset.get("browser_download_url")
                    break
            
            if not download_url:
                self.checkError.emit("未找到可下载的更新包")
                return
            
            # 比较版本
            current = self._parse_version(VERSION)
            latest = self._parse_version(latest_version)
            
            has_update = latest > current
            logger.info(f"当前版本: {VERSION}, 最新版本: {latest_version}, 有更新: {has_update}")
            
            self.checkFinished.emit(has_update, latest_version, download_url, release_notes)
            
        except Exception as e:
            logger.error(f"检查更新失败: {e}")
            self.checkError.emit(f"检查更新失败: {str(e)}")
    
    def _parse_version(self, version_str: str) -> Tuple[int, int, int]:
        """解析版本号，支持 v2.0.5 或 2.0.5 格式"""
        try:
            # 移除 'v' 前缀
            version_str = version_str.lstrip('vV')
            parts = version_str.split('.')
            major = int(parts[0]) if len(parts) > 0 else 0
            minor = int(parts[1]) if len(parts) > 1 else 0
            patch = int(parts[2]) if len(parts) > 2 else 0
            return (major, minor, patch)
        except:
            return (0, 0, 0)


class UpdateDownloader(QThread):
    """下载更新包的线程"""
    
    # 信号：(已下载字节数, 总字节数)
    progressChanged = pyqtSignal(int, int)
    # 信号：(成功, 下载文件路径或错误信息)
    downloadFinished = pyqtSignal(bool, str)
    
    def __init__(self, download_url: str, parent=None):
        super().__init__(parent)
        self.download_url = download_url
        self.save_path = None
        
    def run(self):
        """下载更新文件"""
        try:
            # 创建临时目录
            temp_dir = Path(tempfile.gettempdir()) / "onemore_update"
            temp_dir.mkdir(exist_ok=True)
            
            # 确定文件名
            filename = self.download_url.split('/')[-1]
            self.save_path = temp_dir / filename
            
            logger.info(f"开始下载更新: {self.download_url}")
            logger.info(f"保存路径: {self.save_path}")
            
            # 下载文件
            response = requests.get(self.download_url, stream=True, timeout=30)
            total_size = int(response.headers.get('content-length', 0))
            
            downloaded = 0
            with open(self.save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        self.progressChanged.emit(downloaded, total_size)
            
            logger.info(f"更新包下载完成: {self.save_path}")
            self.downloadFinished.emit(True, str(self.save_path))
            
        except Exception as e:
            logger.error(f"下载更新失败: {e}")
            self.downloadFinished.emit(False, f"下载失败: {str(e)}")


class AppUpdater:
    """应用程序更新管理器"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.checker = None
        self.downloader = None
        
    def check_update(self, callback: Optional[Callable] = None):
        """
        检查更新
        callback: 回调函数，参数为 (has_update, version, download_url, release_notes) 或 (error_msg)
        """
        self.checker = UpdateChecker()
        
        if callback:
            self.checker.checkFinished.connect(
                lambda has_update, ver, url, notes: callback(True, has_update, ver, url, notes)
            )
            self.checker.checkError.connect(
                lambda msg: callback(False, msg)
            )
        
        self.checker.start()
        return self.checker
    
    def download_update(self, download_url: str, progress_callback: Optional[Callable] = None,
                       finish_callback: Optional[Callable] = None):
        """
        下载更新包
        progress_callback: 进度回调，参数为 (downloaded, total)
        finish_callback: 完成回调，参数为 (success, path_or_error)
        """
        self.downloader = UpdateDownloader(download_url)
        
        if progress_callback:
            self.downloader.progressChanged.connect(progress_callback)
        
        if finish_callback:
            self.downloader.downloadFinished.connect(finish_callback)
        
        self.downloader.start()
        return self.downloader
    
    @staticmethod
    def install_update(update_file: str):
        """
        安装更新并重启应用
        update_file: 更新文件路径（.zip 或 .exe）
        
        注意：此功能仅在打包后的环境中可用，开发环境会拒绝执行
        """
        try:
            # 安全检查：禁止在开发环境中执行更新
            if not _is_packaged():
                error_msg = "⚠️ 安全保护：更新功能仅在打包后的应用中可用，开发环境不支持自动更新"
                logger.warning(error_msg)
                logger.info(f"检测环境: sys.frozen={getattr(sys, 'frozen', False)}, __compiled__={globals().get('__compiled__', False)}, sys.executable={sys.executable}")
                raise RuntimeError(error_msg)
            
            update_path = Path(update_file)
            
            if not update_path.exists():
                raise FileNotFoundError(f"更新文件不存在: {update_file}")
            
            logger.info("准备启动更新助手...")

            # 通过当前可执行文件启动更新助手（避免依赖外部 Python）
            if sys.platform == 'win32':
                subprocess.Popen(
                    [sys.executable, "--update-helper", str(update_path)],
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
            else:
                subprocess.Popen([sys.executable, "--update-helper", str(update_path)])
            
            # 延迟退出，让辅助脚本启动
            logger.info("正在退出应用以安装更新...")
            time.sleep(2)
            
            # 退出当前应用
            sys.exit(0)
            
        except Exception as e:
            logger.error(f"安装更新失败: {e}")
            raise

    @staticmethod
    def run_update_helper(update_file: str):
        """更新助手执行逻辑（由打包后的 exe 以参数触发）"""
        update_path = Path(update_file)

        # 计算应用目录
        if _is_packaged():
            app_dir = Path(sys.executable).parent
        else:
            app_dir = Path(ROOTPATH)

        # 生成带时间戳的备份目录
        timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
        backup_dir = app_dir / "backup" / timestamp
        
        # 创建日志文件
        log_dir = app_dir / "appData" / "log"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"update_{timestamp}.txt"
        
        def log_print(msg):
            """同时输出到控制台和日志文件"""
            print(msg)
            try:
                with open(log_file, 'a', encoding='utf-8') as f:
                    f.write(msg + '\n')
            except:
                pass

        log_print("=" * 60)
        log_print("OneMore 自动更新助手")
        log_print("=" * 60)
        log_print(f"更新时间: {timestamp}")
        log_print(f"更新文件: {update_path}")
        log_print(f"应用目录: {app_dir}")
        log_print(f"日志文件: {log_file}")
        log_print("\n等待主程序完全退出...")
        
        # 延长等待时间，确保主程序和所有子进程完全退出
        for i in range(5, 0, -1):
            log_print(f"  倒计时: {i} 秒...")
            time.sleep(1)

        if not update_path.exists():
            raise FileNotFoundError(f"更新文件不存在: {update_path}")

        if update_path.suffix.lower() == '.zip':
            # === 步骤1: 移动所有文件到备份目录 ===
            log_print("\n[1/3] 正在移动所有文件到备份目录...")
            backup_dir.mkdir(parents=True, exist_ok=True)

            for item in list(app_dir.iterdir()):
                # 跳过备份目录自身
                if item.name == "backup":
                    continue
                try:
                    dest = backup_dir / item.name
                    item.rename(dest)
                    log_print(f"  ✓ 已移动: {item.name}")
                except Exception as e:
                    log_print(f"  ✗ 移动失败 {item.name}: {e}")

            # === 步骤2: 解压更新包到应用目录 ===
            log_print("\n[2/3] 正在解压更新包到应用目录...")

            # 更新包已被移动到 backup 中，从 backup 路径读取
            moved_update = backup_dir / update_path.name
            if not moved_update.exists():
                # 如果更新包不在 backup 中（比如在 temp 目录），用原路径
                moved_update = update_path

            with zipfile.ZipFile(moved_update, 'r') as zip_ref:
                zip_ref.extractall(app_dir)
            log_print("  ✓ 更新包已解压")

            # 如果解压后只有一个子目录（如 main.dist），把内容提升到 app_dir
            extracted_items = [p for p in app_dir.iterdir() if p.name != "backup"]
            if len(extracted_items) == 1 and extracted_items[0].is_dir():
                inner_dir = extracted_items[0]
                log_print(f"  → 检测到单层目录 {inner_dir.name}，正在展开...")
                for item in list(inner_dir.iterdir()):
                    dest = app_dir / item.name
                    try:
                        item.rename(dest)
                    except Exception as e:
                        log_print(f"  ✗ 展开失败 {item.name}: {e}")
                # 删除空的内层目录
                try:
                    inner_dir.rmdir()
                except:
                    pass
                log_print("  ✓ 目录已展开")

            # === 步骤3: 从备份恢复用户数据目录 ===
            log_print("\n[3/3] 正在从备份恢复用户数据...")
            restore_dirs = ["app", "appData", "plugins", "tools"]
            for dir_name in restore_dirs:
                backup_item = backup_dir / dir_name
                if not backup_item.exists():
                    continue
                dest_item = app_dir / dir_name
                try:
                    if backup_item.is_dir():
                        if dest_item.exists():
                            shutil.rmtree(dest_item)
                        shutil.copytree(backup_item, dest_item)
                    else:
                        shutil.copy2(backup_item, dest_item)
                    log_print(f"  ✓ 已恢复: {dir_name}")
                except Exception as e:
                    log_print(f"  ✗ 恢复失败 {dir_name}: {e}")

            # 清理更新包
            log_print("\n正在清理临时文件...")
            moved_update.unlink(missing_ok=True)
            update_path.unlink(missing_ok=True)
            log_print("  ✓ 临时文件已清理")

        elif update_path.suffix.lower() == '.exe':
            # 单个 exe 文件的更新（简化版）
            log_print("\n[1/2] 正在备份当前可执行文件...")
            backup_dir.mkdir(parents=True, exist_ok=True)

            current_exe = app_dir / "main.exe"
            if current_exe.exists():
                backup_exe = backup_dir / "main.exe"
                shutil.copy2(current_exe, backup_exe)
                log_print(f"  ✓ 已备份: {current_exe.name}")

            log_print("\n[2/2] 正在替换可执行文件...")
            shutil.copy2(update_path, current_exe)
            log_print(f"  ✓ 已更新: {current_exe.name}")

            update_path.unlink(missing_ok=True)

        log_print("\n" + "=" * 60)
        log_print("✓ 更新完成！")
        log_print("=" * 60)

        # 清理旧备份，只保留最近 3 份
        log_print("\n正在清理旧备份...")
        backup_root = app_dir / "backup"
        if backup_root.exists():
            backups = sorted(
                [d for d in backup_root.iterdir() if d.is_dir()],
                key=lambda d: d.name
            )
            while len(backups) > 3:
                oldest = backups.pop(0)
                try:
                    shutil.rmtree(oldest)
                    log_print(f"  ✓ 已删除旧备份: {oldest.name}")
                except Exception as e:
                    log_print(f"  ✗ 删除旧备份失败 {oldest.name}: {e}")

        log_print("\n正在重启应用...")
        time.sleep(2)

        main_exe = app_dir / "main.exe"
        if main_exe.exists():
            os.startfile(str(main_exe))
        else:
            for exe in app_dir.glob("*.exe"):
                os.startfile(str(exe))
                break
    

