# coding: utf-8
"""
软件更新对话框
显示更新信息、下载进度和安装选项
"""
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from qfluentwidgets import (
    MessageBoxBase, SubtitleLabel, BodyLabel, 
    PrimaryPushButton, PushButton, ProgressBar,
    TextEdit, ScrollArea
)

from ..common.app_updater import AppUpdater
from loguru import logger


class UpdateMessageBox(MessageBoxBase):
    """更新提示对话框"""
    
    def __init__(self, version: str, download_url: str, release_notes: str, parent=None):
        super().__init__(parent)
        self.version = version
        self.download_url = download_url
        self.release_notes = release_notes
        self.updater = AppUpdater()
        
        self.titleLabel = SubtitleLabel(f'发现新版本 {version}', self)
        
        # 更新说明
        self.notesLabel = BodyLabel("更新内容：", self)
        self.notesText = TextEdit(self)
        self.notesText.setPlainText(release_notes)
        self.notesText.setReadOnly(True)
        self.notesText.setMaximumHeight(200)
        
        # 下载进度
        self.progressBar = ProgressBar(self)
        self.progressBar.setVisible(False)
        self.progressLabel = BodyLabel("", self)
        self.progressLabel.setVisible(False)
        
        # 按钮
        self.updateButton = PrimaryPushButton('立即更新', self)
        self.cancelButton = PushButton('稍后提醒', self)
        
        # 添加控件到布局
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.notesLabel)
        self.viewLayout.addWidget(self.notesText)
        self.viewLayout.addWidget(self.progressLabel)
        self.viewLayout.addWidget(self.progressBar)
        
        # 设置按钮布局
        self.yesButton.setParent(None)
        self.cancelButton.setParent(None)
        
        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.updateButton)
        buttonLayout.addWidget(self.cancelButton)
        self.buttonLayout.addLayout(buttonLayout)
        
        # 连接信号
        self.updateButton.clicked.connect(self._on_update_clicked)
        self.cancelButton.clicked.connect(self.reject)
        
        # 设置对话框大小
        self.widget.setMinimumWidth(500)
    
    def _on_update_clicked(self):
        """点击更新按钮"""
        self.updateButton.setEnabled(False)
        self.cancelButton.setEnabled(False)
        self.progressBar.setVisible(True)
        self.progressLabel.setVisible(True)
        self.progressLabel.setText("正在下载更新...")
        
        # 开始下载
        self.updater.download_update(
            self.download_url,
            progress_callback=self._on_download_progress,
            finish_callback=self._on_download_finished
        )
    
    def _on_download_progress(self, downloaded: int, total: int):
        """下载进度更新"""
        if total > 0:
            progress = int(downloaded * 100 / total)
            self.progressBar.setValue(progress)
            
            # 格式化显示
            downloaded_mb = downloaded / 1024 / 1024
            total_mb = total / 1024 / 1024
            self.progressLabel.setText(f"正在下载: {downloaded_mb:.1f}MB / {total_mb:.1f}MB ({progress}%)")
    
    def _on_download_finished(self, success: bool, path_or_error: str):
        """下载完成"""
        if success:
            self.progressLabel.setText("下载完成，准备安装...")
            logger.info(f"更新包下载完成: {path_or_error}")
            
            try:
                # 安装更新（会退出程序）
                AppUpdater.install_update(path_or_error)
            except RuntimeError as e:
                # 开发环境保护错误
                logger.warning(f"无法安装更新: {e}")
                self.progressLabel.setText("⚠️ 开发环境不支持自动更新\n请手动打包后测试此功能")
                self.progressBar.setVisible(False)
                self.cancelButton.setEnabled(True)
                self.cancelButton.setText("确定")
            except Exception as e:
                logger.error(f"安装更新失败: {e}")
                self.progressLabel.setText(f"安装失败: {str(e)}")
                self.updateButton.setEnabled(True)
                self.updateButton.setText("重试")
                self.cancelButton.setEnabled(True)
        else:
            logger.error(f"下载失败: {path_or_error}")
            self.progressLabel.setText(f"下载失败: {path_or_error}")
            self.progressBar.setValue(0)
            self.updateButton.setEnabled(True)
            self.updateButton.setText("重试")
            self.cancelButton.setEnabled(True)


class CheckUpdateMessageBox(MessageBoxBase):
    """手动检查更新对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.updater = AppUpdater()
        
        self.titleLabel = SubtitleLabel('检查更新', self)
        self.statusLabel = BodyLabel("正在检查更新，请稍候...", self)
        
        self.progressBar = ProgressBar(self)
        self.progressBar.setRange(0, 0)  # 不确定进度
        
        # 添加控件
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.statusLabel)
        self.viewLayout.addWidget(self.progressBar)
        
        # 隐藏默认按钮
        self.yesButton.setVisible(False)
        self.cancelButton.setVisible(False)
        
        self.widget.setMinimumWidth(400)
        
        # 开始检查
        self._start_check()
    
    def _start_check(self):
        """开始检查更新"""
        self.updater.check_update(callback=self._on_check_finished)
    
    def _on_check_finished(self, success: bool, *args):
        """检查完成"""
        self.progressBar.setRange(0, 100)
        self.progressBar.setValue(100)
        
        if success:
            has_update, version, download_url, release_notes = args
            if has_update:
                self.statusLabel.setText(f"发现新版本 {version}！")
                # 关闭当前对话框，显示更新对话框
                self.accept()
                update_dialog = UpdateMessageBox(version, download_url, release_notes, self.parent())
                update_dialog.exec()
            else:
                self.statusLabel.setText("当前已是最新版本")
                # 添加关闭按钮
                self.yesButton.setVisible(True)
                self.yesButton.setText("确定")
                self.yesButton.clicked.connect(self.accept)
        else:
            error_msg = args[0]
            self.statusLabel.setText(f"检查失败: {error_msg}")
            # 添加关闭按钮
            self.yesButton.setVisible(True)
            self.yesButton.setText("确定")
            self.yesButton.clicked.connect(self.accept)
