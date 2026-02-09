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
            logger.info(data)
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
            # === 步骤1: 创建备份 ===
            log_print("\n[1/5] 正在备份当前版本...")
            backup_dir.mkdir(parents=True, exist_ok=True)

            items_to_backup = ["appData", "plugins", "tools"]
            for item_name in items_to_backup:
                item_path = app_dir / item_name
                if item_path.exists():
                    backup_item = backup_dir / item_name
                    try:
                        if item_path.is_file():
                            backup_item.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(item_path, backup_item)
                            log_print(f"  ✓ 已备份文件: {item_name}")
                        elif item_path.is_dir():
                            shutil.copytree(item_path, backup_item)
                            log_print(f"  ✓ 已备份目录: {item_name}")
                    except Exception as e:
                        log_print(f"  ✗ 备份失败 {item_name}: {e}")

            # === 步骤2: 解压新版本到临时目录 ===
            log_print("\n[2/5] 正在解压更新包...")
            temp_extract = app_dir / "_update_temp"
            if temp_extract.exists():
                shutil.rmtree(temp_extract)
            temp_extract.mkdir(exist_ok=True)

            with zipfile.ZipFile(update_path, 'r') as zip_ref:
                zip_ref.extractall(temp_extract)
            log_print("  ✓ 更新包已解压到临时目录")

            extract_dirs = list(temp_extract.iterdir())
            if len(extract_dirs) == 1 and extract_dirs[0].is_dir():
                source_dir = extract_dirs[0]
            else:
                source_dir = temp_extract

            log_print(f"  ✓ 更新文件源目录: {source_dir.name}")

            # === 步骤3: 清理旧版本文件（保留备份的目录）===
            log_print("\n[3/5] 正在清理旧版本文件...")
            protected_items = ["backup", "_update_temp", "appData", "plugins", "tools"]
            failed_items = []
            
            for item in app_dir.iterdir():
                if item.name not in protected_items:
                    deleted = False
                    # 尝试删除 3 次
                    for attempt in range(3):
                        try:
                            if item.is_file():
                                item.unlink()
                                log_print(f"  ✓ 已删除文件: {item.name}")
                                deleted = True
                                break
                            elif item.is_dir():
                                shutil.rmtree(item)
                                log_print(f"  ✓ 已删除目录: {item.name}")
                                deleted = True
                                break
                        except PermissionError:
                            if attempt < 2:
                                time.sleep(1)  # 等待 1 秒后重试
                                continue
                            # 最后一次尝试失败，使用 Windows 延迟删除
                            try:
                                # 移动到临时目录，标记为待删除
                                trash_dir = app_dir / "_to_delete"
                                trash_dir.mkdir(exist_ok=True)
                                dest = trash_dir / f"{item.name}_{int(time.time())}"
                                item.rename(dest)
                                log_print(f"  → 已移至待删除目录: {item.name}")
                                failed_items.append(item.name)
                            except Exception as e2:
                                log_print(f"  ✗ 无法处理 {item.name}: {e2}")
                                failed_items.append(item.name)
                        except Exception as e:
                            log_print(f"  ✗ 删除失败 {item.name}: {e}")
                            failed_items.append(item.name)
                            break
            
            if failed_items:
                log_print(f"\n  ⚠️  部分文件无法立即删除，已移至 _to_delete 目录")
                log_print(f"  这些文件将在下次启动时被清理")

            # === 步骤4: 复制新版本文件 ===
            log_print("\n[4/5] 正在安装新版本...")
            for item in source_dir.iterdir():
                dest = app_dir / item.name

                if item.name in ["appData", "plugins", "tools"] and dest.exists():
                    log_print(f"  → 跳过 {item.name} (保留现有版本)")
                    continue

                try:
                    if item.is_file():
                        # 如果目标文件存在且无法删除，先尝试删除 .old 文件
                        if dest.exists():
                            try:
                                dest.unlink()
                            except PermissionError:
                                # 无法删除，尝试用新文件覆盖
                                pass
                        shutil.copy2(item, dest)
                        log_print(f"  ✓ 已复制文件: {item.name}")
                    elif item.is_dir():
                        if dest.exists():
                            try:
                                shutil.rmtree(dest)
                            except:
                                # 目录无法删除，跳过
                                log_print(f"  → 跳过 {item.name} (目录被占用)")
                                continue
                        shutil.copytree(item, dest)
                        log_print(f"  ✓ 已复制目录: {item.name}")
                except Exception as e:
                    log_print(f"  ✗ 复制失败 {item.name}: {e}")

            # === 步骤5: 恢复配置文件 ===
            log_print("\n[5/5] 正在恢复用户配置...")
            backup_config = backup_dir / "appData" / "config.json"
            if backup_config.exists():
                dest_config = app_dir / "appData" / "config.json"
                dest_config.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(backup_config, dest_config)
                log_print("  ✓ 已恢复配置文件")

            log_print("\n正在清理临时文件...")
            shutil.rmtree(temp_extract, ignore_errors=True)
            update_path.unlink(missing_ok=True)
            
            # 清理 _to_delete 目录（如果存在）
            trash_dir = app_dir / "_to_delete"
            if trash_dir.exists():
                try:
                    shutil.rmtree(trash_dir)
                    log_print("  ✓ 已清理待删除目录")
                except:
                    log_print("  → 待删除目录将在下次启动时清理")
            
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
        log_print("\n正在重启应用...")
        time.sleep(2)

        main_exe = app_dir / "main.exe"
        if main_exe.exists():
            os.startfile(str(main_exe))
        else:
            for exe in app_dir.glob("*.exe"):
                os.startfile(str(exe))
                break
    
    @staticmethod
    def _create_update_helper(update_file: Path) -> Path:
        """创建更新辅助脚本"""
        
        # 确定当前可执行文件路径和应用根目录
        if _is_packaged():
            # 打包后的 exe
            current_exe = Path(sys.executable)
            app_dir = current_exe.parent
        else:
            # 开发模式
            app_dir = Path(ROOTPATH)
            current_exe = app_dir / "main.exe"  # 假设打包后的名称
        
        # 辅助脚本内容
        helper_content = f'''# coding: utf-8
"""
OneMore 自动更新助手
此脚本负责备份、替换和恢复应用程序文件
"""
import os
import sys
import time
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

def main():
    print("=" * 60)
    print("OneMore 自动更新助手")
    print("=" * 60)
    print("\\n等待主程序完全退出...")
    time.sleep(3)
    
    update_file = Path(r"{update_file}")
    app_dir = Path(r"{app_dir}")
    
    # 生成带时间戳的备份目录
    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    backup_dir = app_dir / "backup" / timestamp
    
    try:
        print(f"\\n更新文件: {{update_file}}")
        print(f"应用目录: {{app_dir}}")
        print(f"备份目录: {{backup_dir}}")
        
        if not update_file.exists():
            raise FileNotFoundError(f"更新文件不存在: {{update_file}}")
        
        if update_file.suffix.lower() == '.zip':
            # === 步骤1: 创建备份 ===
            print("\\n[1/5] 正在备份当前版本...")
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # 需要备份的目录和文件
            items_to_backup = [
                "appData",      # 配置文件目录
                "plugins",      # 插件目录
                "tools"         # 工具目录（如果存在）
            ]
            
            for item_name in items_to_backup:
                item_path = app_dir / item_name
                if item_path.exists():
                    backup_item = backup_dir / item_name
                    try:
                        if item_path.is_file():
                            backup_item.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(item_path, backup_item)
                            print(f"  ✓ 已备份文件: {{item_name}}")
                        elif item_path.is_dir():
                            shutil.copytree(item_path, backup_item)
                            print(f"  ✓ 已备份目录: {{item_name}}")
                    except Exception as e:
                        print(f"  ✗ 备份失败 {{item_name}}: {{e}}")
            
            # === 步骤2: 解压新版本到临时目录 ===
            print("\\n[2/5] 正在解压更新包...")
            temp_extract = app_dir / "_update_temp"
            if temp_extract.exists():
                shutil.rmtree(temp_extract)
            temp_extract.mkdir(exist_ok=True)
            
            with zipfile.ZipFile(update_file, 'r') as zip_ref:
                zip_ref.extractall(temp_extract)
            print(f"  ✓ 更新包已解压到临时目录")
            
            # 查找解压后的主目录（可能是 main.dist 或其他）
            extract_dirs = list(temp_extract.iterdir())
            if len(extract_dirs) == 1 and extract_dirs[0].is_dir():
                source_dir = extract_dirs[0]
            else:
                source_dir = temp_extract
            
            print(f"  ✓ 更新文件源目录: {{source_dir.name}}")
            
            # === 步骤3: 删除旧版本文件（保留备份的目录）===
            print("\\n[3/5] 正在清理旧版本文件...")
            protected_items = ["backup", "_update_temp", "appData", "plugins", "tools"]
            
            for item in app_dir.iterdir():
                if item.name not in protected_items:
                    try:
                        if item.is_file():
                            item.unlink()
                            print(f"  ✓ 已删除文件: {{item.name}}")
                        elif item.is_dir():
                            shutil.rmtree(item)
                            print(f"  ✓ 已删除目录: {{item.name}}")
                    except Exception as e:
                        print(f"  ✗ 删除失败 {{item.name}}: {{e}}")
            
            # === 步骤4: 复制新版本文件 ===
            print("\\n[4/5] 正在安装新版本...")
            for item in source_dir.iterdir():
                dest = app_dir / item.name
                
                # 跳过已存在的受保护目录
                if item.name in ["appData", "plugins", "tools"] and dest.exists():
                    print(f"  → 跳过 {{item.name}} (保留现有版本)")
                    continue
                
                try:
                    if item.is_file():
                        shutil.copy2(item, dest)
                        print(f"  ✓ 已复制文件: {{item.name}}")
                    elif item.is_dir():
                        if dest.exists():
                            shutil.rmtree(dest)
                        shutil.copytree(item, dest)
                        print(f"  ✓ 已复制目录: {{item.name}}")
                except Exception as e:
                    print(f"  ✗ 复制失败 {{item.name}}: {{e}}")
            
            # === 步骤5: 恢复配置文件（如果新版本覆盖了）===
            print("\\n[5/5] 正在恢复用户配置...")
            
            # 从备份恢复 appData/config.json
            backup_config = backup_dir / "appData" / "config.json"
            if backup_config.exists():
                dest_config = app_dir / "appData" / "config.json"
                dest_config.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(backup_config, dest_config)
                print(f"  ✓ 已恢复配置文件")
            
            # 清理临时文件
            print("\\n正在清理临时文件...")
            shutil.rmtree(temp_extract, ignore_errors=True)
            update_file.unlink(missing_ok=True)
            print("  ✓ 临时文件已清理")
            
        elif update_file.suffix.lower() == '.exe':
            # 单个 exe 文件的更新（简化版）
            print("\\n[1/2] 正在备份当前可执行文件...")
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            current_exe = app_dir / "main.exe"
            if current_exe.exists():
                backup_exe = backup_dir / "main.exe"
                shutil.copy2(current_exe, backup_exe)
                print(f"  ✓ 已备份: {{current_exe.name}}")
            
            print("\\n[2/2] 正在替换可执行文件...")
            shutil.copy2(update_file, current_exe)
            print(f"  ✓ 已更新: {{current_exe.name}}")
            
            update_file.unlink(missing_ok=True)
        
        print("\\n" + "=" * 60)
        print("✓ 更新完成！")
        print("=" * 60)
        print("\\n正在重启应用...")
        time.sleep(2)
        
        # 重启应用
        main_exe = app_dir / "main.exe"
        if main_exe.exists():
            os.startfile(str(main_exe))
        else:
            # 尝试查找其他可执行文件
            for exe in app_dir.glob("*.exe"):
                os.startfile(str(exe))
                break
        
        print("\\n应用已重启，更新助手将在 3 秒后自动关闭...")
        time.sleep(3)
        
    except Exception as e:
        print(f"\\n✗ 更新失败: {{e}}")
        print("\\n可以尝试从备份目录手动恢复:")
        print(f"  {{backup_dir}}")
        input("\\n按回车键退出...")
        sys.exit(1)

if __name__ == '__main__':
    main()
'''
        
        # 保存辅助脚本
        helper_path = Path(tempfile.gettempdir()) / "onemore_updater.py"
        helper_path.write_text(helper_content, encoding='utf-8')
        
        logger.info(f"更新助手脚本已创建: {helper_path}")
        return helper_path
