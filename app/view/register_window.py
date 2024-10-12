# coding:utf-8
import sys
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QPainter, QColor, QIcon
from PyQt6.QtWidgets import QWidget, QApplication, QHBoxLayout, QVBoxLayout

from qfluentwidgets import (MSFluentTitleBar, isDarkTheme, ImageLabel, BodyLabel, LineEdit,
                            PasswordLineEdit, PrimaryPushButton, HyperlinkButton, CheckBox, InfoBar,
                            InfoBarPosition, setThemeColor)
from ..common import resource
from ..common.license_service import LicenseService
from ..common.config import cfg
from .main_window import MainWindow
from ..common.logging import *

def isWin11():
    return sys.platform == 'win32' and sys.getwindowsversion().build >= 22000


if isWin11():
    from qframelesswindow import AcrylicWindow as Window
else:
    from qframelesswindow import FramelessWindow as Window


class RegisterWindow(Window):
    """ Register window """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        setThemeColor('#28afe9')
        self.setTitleBar(MSFluentTitleBar(self))
        self.register = LicenseService()

        self.imageLabel = ImageLabel(':/app/images/background.jpg', self)
        self.iconLabel = ImageLabel(':/app/images/logo.png', self)

        self.emailLabel = BodyLabel(self.tr('Email'), self)
        self.emailLineEdit = LineEdit(self)

        self.passwordLabel = BodyLabel(self.tr('Password'), self)
        self.passwordLineEdit = PasswordLineEdit(self)

        self.rememberCheckBox = CheckBox(self.tr('Remember me'), self)

        self.loginButton = PrimaryPushButton(self.tr('Login'), self)

        self.hBoxLayout = QHBoxLayout(self)
        self.vBoxLayout = QVBoxLayout()

        self.__initWidgets()

    def __initWidgets(self):
        self.titleBar.maxBtn.hide()
        self.titleBar.setDoubleClickEnabled(False)
        self.rememberCheckBox.setChecked(cfg.get(cfg.rememberMe))

        self.emailLineEdit.setPlaceholderText('example@example.com')
        self.passwordLineEdit.setPlaceholderText('••••••••••••')

        if self.rememberCheckBox.isChecked():
            self.emailLineEdit.setText(cfg.get(cfg.email))
            self.passwordLineEdit.setText(cfg.get(cfg.password))

        self.__connectSignalToSlot()
        self.__initLayout()

        if isWin11():
            self.windowEffect.setMicaEffect(self.winId(), isDarkTheme())
        else:
            color = QColor(25, 33, 42) if isDarkTheme(
            ) else QColor(240, 244, 249)
            self.setStyleSheet(f"RegisterWindow{{background: {color.name()}}}")

        self.setWindowTitle('OneMore')
        self.setWindowIcon(QIcon(":/app/images/logo.png"))
        self.resize(1000, 650)

        self.titleBar.titleLabel.setStyleSheet("""
            QLabel{
                background: transparent;
                font: 13px 'Segoe UI';
                padding: 0 4px;
                color: white
            }
        """)

        desktop = QApplication.screens()[0].availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)

        self.titleBar.raise_()

    def __initLayout(self):
        self.imageLabel.scaledToHeight(650)
        self.iconLabel.scaledToHeight(100)

        self.hBoxLayout.addWidget(self.imageLabel)
        self.hBoxLayout.addLayout(self.vBoxLayout)

        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setContentsMargins(20, 0, 20, 0)
        self.vBoxLayout.setSpacing(0)
        self.hBoxLayout.setSpacing(0)

        self.vBoxLayout.addStretch(1)
        self.vBoxLayout.addWidget(
            self.iconLabel, 0, Qt.AlignmentFlag.AlignHCenter)
        self.vBoxLayout.addSpacing(38)
        self.vBoxLayout.addWidget(self.emailLabel)
        self.vBoxLayout.addSpacing(11)
        self.vBoxLayout.addWidget(self.emailLineEdit)
        self.vBoxLayout.addSpacing(12)
        self.vBoxLayout.addWidget(self.passwordLabel)
        self.vBoxLayout.addSpacing(11)
        self.vBoxLayout.addWidget(self.passwordLineEdit)
        self.vBoxLayout.addSpacing(12)
        self.vBoxLayout.addWidget(self.rememberCheckBox)
        self.vBoxLayout.addSpacing(15)
        self.vBoxLayout.addWidget(self.loginButton)
        self.vBoxLayout.addSpacing(30)
        self.vBoxLayout.addStretch(1)

    def __connectSignalToSlot(self):
        self.loginButton.clicked.connect(self._login)
        self.rememberCheckBox.stateChanged.connect(
            lambda: cfg.set(cfg.rememberMe, self.rememberCheckBox.isChecked()))

    def _login(self):
        code = self.passwordLineEdit.text().strip()

        if not self.register.validate(code, self.emailLineEdit.text()):
            InfoBar.error(
                self.tr("Login failed"),
                self.tr('Please check your password and email address again'),
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self.window()
            )
        else:
            InfoBar.success(
                self.tr("Success"),
                self.tr('Login successful'),
                position=InfoBarPosition.TOP,
                parent=self.window()
            )

            if cfg.get(cfg.rememberMe):
                cfg.set(cfg.email, self.emailLineEdit.text().strip())
                cfg.set(cfg.password, code)

            self.loginButton.setDisabled(True)
            QTimer.singleShot(1500, self._showMainWindow)

    def _showMainWindow(self):
        self.close()
        setThemeColor('#009faa')

        w = MainWindow()
        w.show()
