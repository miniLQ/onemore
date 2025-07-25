from PyQt6.QtCore import Qt, QThread
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from qfluentwidgets import CardWidget
import sys
from pathlib import Path
import os
import subprocess
import re

from PyQt6.QtCore import Qt, QPoint, QSize, QUrl, QRect, QPropertyAnimation, pyqtSignal, QObject
from PyQt6.QtGui import QIcon, QFont, QColor, QPainter
from PyQt6.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QGraphicsOpacityEffect,QFileDialog

from qfluentwidgets import (CardWidget, setTheme, Theme, IconWidget, BodyLabel, CaptionLabel, PushButton,
                            TransparentToolButton, FluentIcon, RoundMenu, Action, ElevatedCardWidget,
                            ImageLabel, isDarkTheme, FlowLayout, MSFluentTitleBar, SimpleCardWidget,
                            HeaderCardWidget, InfoBarIcon, HyperlinkLabel, HorizontalFlipView, EditableComboBox,
                            PrimaryPushButton, TitleLabel, PillPushButton, setFont, ScrollArea,
                            VerticalSeparator, MSFluentWindow, NavigationItemPosition, GroupHeaderCardWidget,
                            ComboBox, SearchLineEdit, SubtitleLabel, StateToolTip, LineEdit, Flyout)

from qfluentwidgets.components.widgets.acrylic_label import AcrylicBrush

from app.common.config import ROOTPATH
from app.common.logging import logger
from app.common.utils import linuxPath2winPath

NOC_DECODE_TOOLS_PATH = os.path.join(ROOTPATH, 'tools', 'NOC_decode')
PYTHON_BIN = os.path.join(ROOTPATH, 'tools', 'android-sdk', 'python', 'bin', 'python.exe')

# 获取当前文件的路径
current_path = Path(__file__).resolve().parent
# resource文件夹的路径, 位于当前文件的上两级目录
resource_path = current_path.parent.parent / 'resource'


def isWin11():
    return sys.platform == 'win32' and sys.getwindowsversion().build >= 22000


if isWin11():
    from qframelesswindow import AcrylicWindow as Window
else:
    from qframelesswindow import FramelessWindow as Window

class StatisticsWidget(QWidget):
    """ Statistics widget """

    def __init__(self, title: str, value: str, parent=None):
        super().__init__(parent=parent)
        self.titleLabel = CaptionLabel(title, self)
        self.valueLabel = BodyLabel(value, self)
        self.vBoxLayout = QVBoxLayout(self)

        self.vBoxLayout.setContentsMargins(16, 0, 16, 0)
        self.vBoxLayout.addWidget(self.valueLabel, 0, Qt.AlignmentFlag.AlignTop)
        self.vBoxLayout.addWidget(self.titleLabel, 0, Qt.AlignmentFlag.AlignBottom)

        setFont(self.valueLabel, 18, QFont.Weight.DemiBold)
        self.titleLabel.setTextColor(QColor(96, 96, 96), QColor(206, 206, 206))


class AppInfoCard(SimpleCardWidget):
    """ App information card """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.iconLabel = ImageLabel(":/qfluentwidgets/images/logo.png", self)
        self.iconLabel.setBorderRadius(8, 8, 8, 8)
        self.iconLabel.scaledToWidth(120)

        self.nameLabel = TitleLabel('NOC decode tool', self)

        #self.installButton = PrimaryPushButton('执行', self)
        #self.installButton.clicked.connect(self.installButtonClicked)
        #self.installButtonStateTooltip = None

        #self.companyLabel = HyperlinkLabel(
        #    QUrl('https://qfluentwidgets.com'), 'Shokokawaii Inc.', self)
        self.companyLabel = CaptionLabel('@Designed by iliuqi.', self)
        #self.installButton.setFixedWidth(160)

        #self.scoreWidget = StatisticsWidget('平均', '5.0', self)
        #self.separator = VerticalSeparator(self)
        #self.commentWidget = StatisticsWidget('评论数', '3K', self)

        self.descriptionLabel = BodyLabel(
            'NOC decode tool 是高通平台开发提供给研发人员进行NOC error log的解析使用的一个工具', self)
        self.descriptionLabel.setWordWrap(True)

        self.tagButton = PillPushButton('QCOM', self)
        self.tagButton.setCheckable(False)
        setFont(self.tagButton, 12)
        self.tagButton.setFixedSize(80, 32)

        self.tagButton2 = PillPushButton('NOC', self)
        self.tagButton2.setCheckable(False)
        setFont(self.tagButton2, 12)
        self.tagButton2.setFixedSize(80, 32)

        #self.shareButton = TransparentToolButton(FluentIcon.SHARE, self)
        #self.shareButton.setFixedSize(32, 32)
        #self.shareButton.setIconSize(QSize(14, 14))

        self.hBoxLayout = QHBoxLayout(self)
        self.vBoxLayout = QVBoxLayout()
        self.topLayout = QHBoxLayout()
        self.statisticsLayout = QHBoxLayout()
        self.buttonLayout = QHBoxLayout()

        self.initLayout()
        self.setBorderRadius(8)

    def initLayout(self):
        self.hBoxLayout.setSpacing(30)
        self.hBoxLayout.setContentsMargins(34, 24, 24, 24)
        self.hBoxLayout.addWidget(self.iconLabel)
        self.hBoxLayout.addLayout(self.vBoxLayout)

        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setSpacing(0)

        # name label and install button
        self.vBoxLayout.addLayout(self.topLayout)
        self.topLayout.setContentsMargins(0, 0, 0, 0)
        self.topLayout.addWidget(self.nameLabel)
        #self.topLayout.addWidget(self.installButton, 0, Qt.AlignmentFlag.AlignRight)

        # company label
        self.vBoxLayout.addSpacing(3)
        self.vBoxLayout.addWidget(self.companyLabel)

        # statistics widgets
        self.vBoxLayout.addSpacing(20)
        self.vBoxLayout.addLayout(self.statisticsLayout)
        self.statisticsLayout.setContentsMargins(0, 0, 0, 0)
        self.statisticsLayout.setSpacing(10)
        #self.statisticsLayout.addWidget(self.scoreWidget)
        #self.statisticsLayout.addWidget(self.separator)
        #self.statisticsLayout.addWidget(self.commentWidget)
        self.statisticsLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # description label
        self.vBoxLayout.addSpacing(20)
        self.vBoxLayout.addWidget(self.descriptionLabel)

        # button
        self.vBoxLayout.addSpacing(12)
        self.buttonLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.addLayout(self.buttonLayout)
        self.buttonLayout.addWidget(self.tagButton, 0, Qt.AlignmentFlag.AlignLeft)
        self.buttonLayout.addWidget(self.tagButton2, 1, Qt.AlignmentFlag.AlignLeft)


class  Worker(QThread):
    signal = pyqtSignal(str)

    def __init__(self, command, shell=True):
        super().__init__()
        self.command = command
        self.shell = shell

    def run(self):
        logger.info("Worker Thread ID: {}".format(QThread.currentThreadId()))
        logger.info("Run command: {}".format(self.command))

        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        if self.shell == True:
            command = "start cmd /k {}".format(self.command)
        else:
            command = self.command
        
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        
        while True:
            line = process.stdout.readline()
            if not line:
                break
            logger.info(line.decode('gbk').strip())

        self.signal.emit("SUCCESS")
        #self.signal.emit("ERROR")


class DescriptionCard(HeaderCardWidget):
    """ Description card """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.descriptionLabel = BodyLabel(
            'NOC decode tool 是高通平台开发提供给研发人员进行NOC error log的解析使用的一个工具。\n'
            '本软件集成了一部分的board的配置文件，如果没有你需要的，请从项目代码中复制board配置文件置于NOC_decode/目录下', self)

        self.descriptionLabel.setWordWrap(True)
        self.viewLayout.addWidget(self.descriptionLabel)
        self.setTitle('描述')
        self.setBorderRadius(8)

class SettinsCard(GroupHeaderCardWidget):

    def __init__(self, parent=None, parentvBoxLayout=None):
        super().__init__(parent)
        
        self.parentvBoxLayout = parentvBoxLayout

        self.setTitle("基本设置")
        self.setBorderRadius(8)

        # 初始化参数
        self.inputfile = ""
        self.output_path = ""

        # 设置状态提示
        self.stateTooltip = None
        self.bottomStateLayout = QHBoxLayout()

        # 设置Button的点击事件
        # 选择board

        # 显示终端部件
        self.comboBox = ComboBox()
        
        # 平台选择部件
        self.platformComboBox = ComboBox()

        # 增加文件选择部件
        self.inputchoosebutton = PushButton("选择")
        self.outputchoosebutton = PushButton("选择")

        self.inputchoosebutton.setFixedWidth(120)
        self.outputchoosebutton.setFixedWidth(120)

        self.inputchoosebutton.clicked.connect(self.chooseInputFileClicked)
        self.outputchoosebutton.clicked.connect(self.chooseOutputFileClicked)

        self.comboBox.setFixedWidth(120)
        self.comboBox.addItems(["始终显示", "始终隐藏"])
        # 设置comboBox的选择点击事件
        self.comboBox.currentIndexChanged.connect(self.comboBoxClicked)

        self.platformComboBox.setPlaceholderText("选择平台")

        # TODO: 从配置文件中读取平台信息
        # items = ['khaje', 'parrot', 'pitti']
        # 查询NOC_DECODE_TOOLS_PATH下以data_开头，以.py结尾的文件
        items = [file.split('_')[1].split('.')[0] for file in os.listdir(NOC_DECODE_TOOLS_PATH) if file.startswith('data_') and file.endswith('.py')]

        self.platformComboBox.setFixedWidth(120)
     
    
        self.platformComboBox.addItems(items)
           # 设置默认值
        self.platformComboBox.setCurrentIndex(-1)
        # 设置platformComboBox的编辑事件
        #self.platformComboBox.currentTextChanged.connect(logger.info)
        self.platformComboBox.currentIndexChanged.connect(self.platformComboBoxClicked)



        # 底部运行按钮以及提示
        self.hintIcon = IconWidget(InfoBarIcon.INFORMATION)
        self.hintLabel = BodyLabel("点击运行按钮开始解析")
        self.runButton = PrimaryPushButton(FluentIcon.PLAY_SOLID, "运行")
        self.bottomLayout = QHBoxLayout()

        # 设置底部工具栏布局
        self.hintIcon.setFixedSize(16, 16)
        self.bottomLayout.setSpacing(10)
        self.bottomLayout.setContentsMargins(24, 15, 24, 20)
        self.bottomLayout.addWidget(self.hintIcon, 0, Qt.AlignmentFlag.AlignLeft)
        self.bottomLayout.addWidget(self.hintLabel, 0, Qt.AlignmentFlag.AlignLeft)
        self.bottomLayout.addStretch(1)
        self.bottomLayout.addWidget(self.runButton, 0, Qt.AlignmentFlag.AlignRight)
        self.bottomLayout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        # 设置底部状态布局
        self.bottomStateLayout.setSpacing(10)
        self.bottomStateLayout.setContentsMargins(24, 15, 24, 20)
        self.bottomStateLayout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.bottomStateLayout.addStretch(1)

        self.inputfilegroup = self.addGroup("{}/images/Joystick.svg".format(resource_path), "输入文件", "选择NOC error log文件", self.inputchoosebutton)
        self.outputgroup = self.addGroup("{}/images/Rocket.svg".format(resource_path), "输出文件夹", "选择输出文件夹", self.outputchoosebutton)

        self.addGroup("{}/images/Joystick.svg".format(resource_path), "Platform", "选择board", self.platformComboBox)

        self.addGroup("{}/images/Joystick.svg".format(resource_path), "运行终端", "设置是否显示命令行终端", self.comboBox)
        
        self.vBoxLayout.addLayout(self.bottomLayout)

        # 设置运行按钮的点击事件
        self.runButton.clicked.connect(self.runButtonClicked)

    def chooseInputFileClicked(self):
        logger.info("Choose Input File Clicked")
        self.inputfile, _ = QFileDialog.getOpenFileName(self, "选择NOC error log文件", "", "All Files (*)")
        logger.info("Noc error log file: {}".format(self.inputfile))
        if self.inputfile == "":
            self.inputchoosebutton.setText("选择")
            self.inputfilegroup.setContent("选择NOC error log文件")
        else:
            # 设置chooseButton的文字显示已选择
            self.inputchoosebutton.setText("已选择")
            self.inputfilegroup.setContent(self.inputfile)

    def chooseOutputFileClicked(self):
        logger.info("Choose Output File Clicked")
        self.output_path = QFileDialog.getExistingDirectory(self, "选择输出文件夹", "")
        logger.info("Output path: {}".format(self.output_path))
        if self.output_path == "":
            self.outputchoosebutton.setText("选择")
            self.outputgroup.setContent("选择输出文件夹")
        else:
            # 设置chooseButton的文字显示已选择
            self.outputchoosebutton.setText("已选择")
            self.outputgroup.setContent(self.output_path)


    def comboBoxClicked(self, index):
        logger.info("ComboBox Clicked: ".format(index))
        # 打印当前选择的值
        logger.info("Current Index: ".format(self.comboBox.currentText()))

    def platformComboBoxClicked(self, index):
        logger.info("Platform ComboBox Clicked: {}".format(index))
        # 打印当前选择的值
        logger.info("Current Index: {}".format(self.platformComboBox.currentText()))

    def showNoParametersFlyout(self):
        Flyout.create(
            icon=InfoBarIcon.ERROR,
            title='Some parameters maybe none',
            content="请检查所有的参数是否都已经填写",
            target=self.runButton,
            parent=self.window()
        )
    def showNoSelectPlatformFlyout(self):
        Flyout.create(
            icon=InfoBarIcon.ERROR,
            title='Board is not selected',
            content="请先选择board",
            target=self.runButton,
            parent=self.window()
        )

    def customSignalHandler(self, value):
        # 接收到解析命令结束的信号
        logger.info("Custom signal handler: {}".format(value))
        if value == "SUCCESS":
            self.stateTooltip.setContent('解析完成')
            self.stateTooltip.setState(True)
            self.runButton.setEnabled(True)
            self.stateTooltip.show()

        elif value == "ERROR":
            self.stateTooltip.setContent('解析失败')
            self.stateTooltip.setState(False)
            self.runButton.setEnabled(True)
            self.stateTooltip.show()
        else:
            logger.info(value)

        # 打开输出目录
        #os.system("start {}".format(self.output_path))

    def start_task(self, command, shell):
        logger.info("Start task")
        self.worker = Worker(command, shell=shell)
        self.worker.signal.connect(self.customSignalHandler)
        self.worker.start()

    def runButtonClicked(self):
        logger.info("Run Button Clicked")
        # 获取chooseButton/ vmlinuxButton/ comboBox/ platformComboBox/ lineEdit的值
        logger.info("platform: {}".format(self.platformComboBox.currentText()))
        logger.info('Noc error log file: {}'.format(self.inputfile))
        logger.info('Output path: {}'.format(self.output_path))

        # 判断是否为空
        if self.inputfile == "" or self.output_path == "" or self.platformComboBox.currentText() == "":
            self.showNoParametersFlyout()
            return

        if self.comboBox.currentText() == "始终显示":
            shell = True
        else:
            shell = False

        logger.info("Display terminal: ".format(shell))

        self.stateTooltip = StateToolTip('正在解析', '客官请耐心等待哦~~', self)
        # 状态提示放到中心位置
        self.bottomStateLayout.addWidget(self.stateTooltip, 0, Qt.AlignmentFlag.AlignRight)
        self.vBoxLayout.addLayout(self.bottomStateLayout)
        # 显示状态提示
        self.stateTooltip.show()

        # runbuton按钮设置为不可点击
        self.runButton.setDisabled(True)

        decodefile = linuxPath2winPath(os.path.join(NOC_DECODE_TOOLS_PATH, "NoC_error_decode_log.py"))

        command = "{} {} {} {} -o {}".format(PYTHON_BIN,
            decodefile, self.platformComboBox.currentText(), self.inputfile, self.output_path)
        self.start_task(command, shell)
    

class LightBox(QWidget):
    """ Light box """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        if isDarkTheme():
            tintColor = QColor(32, 32, 32, 200)
        else:
            tintColor = QColor(255, 255, 255, 160)

        self.acrylicBrush = AcrylicBrush(self, 30, tintColor, QColor(0, 0, 0, 0))

        self.opacityEffect = QGraphicsOpacityEffect(self)
        self.opacityAni = QPropertyAnimation(self.opacityEffect, b"opacity", self)
        self.opacityEffect.setOpacity(1)
        self.setGraphicsEffect(self.opacityEffect)

        self.vBoxLayout = QVBoxLayout(self)
        self.closeButton = TransparentToolButton(FluentIcon.CLOSE, self)
        self.flipView = HorizontalFlipView(self)
        self.nameLabel = BodyLabel('屏幕截图 1', self)
        self.pageNumButton = PillPushButton('1 / 4', self)

        self.pageNumButton.setCheckable(False)
        self.pageNumButton.setFixedSize(80, 32)
        setFont(self.nameLabel, 16, QFont.Weight.DemiBold)

        self.closeButton.setFixedSize(32, 32)
        self.closeButton.setIconSize(QSize(14, 14))
        self.closeButton.clicked.connect(self.fadeOut)

        self.vBoxLayout.setContentsMargins(26, 28, 26, 28)
        self.vBoxLayout.addWidget(self.closeButton, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        self.vBoxLayout.addWidget(self.flipView, 1)
        self.vBoxLayout.addWidget(self.nameLabel, 0, Qt.AlignmentFlag.AlignHCenter)
        self.vBoxLayout.addSpacing(10)
        self.vBoxLayout.addWidget(self.pageNumButton, 0, Qt.AlignmentFlag.AlignHCenter)

        self.flipView.addImages([
            '{}/images/shoko1.jpg'.format(resource_path), '{}/images/shoko2.jpg'.format(resource_path),
            '{}/images/shoko3.jpg'.format(resource_path), '{}/images/shoko4.jpg'.format(resource_path),
        ])
        self.flipView.currentIndexChanged.connect(self.setCurrentIndex)

    def setCurrentIndex(self, index: int):
        self.nameLabel.setText(f'屏幕截图 {index + 1}')
        self.pageNumButton.setText(f'{index + 1} / {self.flipView.count()}')
        self.flipView.setCurrentIndex(index)

    def paintEvent(self, e):
        if self.acrylicBrush.isAvailable():
            return self.acrylicBrush.paint()

        painter = QPainter(self)
        painter.setPen(Qt.NoPen)
        if isDarkTheme():
            painter.setBrush(QColor(32, 32, 32))
        else:
            painter.setBrush(QColor(255, 255, 255))

        painter.drawRect(self.rect())

    def resizeEvent(self, e):
        w = self.width() - 52
        self.flipView.setItemSize(QSize(w, w * 9 // 16))

    def fadeIn(self):
        rect = QRect(self.mapToGlobal(QPoint()), self.size())
        self.acrylicBrush.grabImage(rect)

        self.opacityAni.setStartValue(0)
        self.opacityAni.setEndValue(1)
        self.opacityAni.setDuration(150)
        self.opacityAni.start()
        self.show()

    def fadeOut(self):
        self.opacityAni.setStartValue(1)
        self.opacityAni.setEndValue(0)
        self.opacityAni.setDuration(150)
        self.opacityAni.finished.connect(self._onAniFinished)
        self.opacityAni.start()

    def _onAniFinished(self):
        self.opacityAni.finished.disconnect()
        self.hide()

class NocErrFileDecodeCardsInfo(ScrollArea):
    """ Linux Ramdump Parser Subinterface """

    def __init__(self, parent=None, routeKey=None):
        super().__init__(parent=parent)

        self.view = QWidget(self)

        self.routeKey = routeKey

        self.vBoxLayout = QVBoxLayout(self.view)
        self.appCard = AppInfoCard(parent=self)
        #self.galleryCard = GalleryCard(self)
        self.descriptionCard = DescriptionCard(self)
        self.settingCard = SettinsCard(self, parentvBoxLayout=self.vBoxLayout)
        #self.systemCard = SystemRequirementCard(self)

        self.lightBox = LightBox(self)
        self.lightBox.hide()
        #self.galleryCard.flipView.itemClicked.connect(self.showLightBox)

        self.setWidget(self.view)
        self.setWidgetResizable(True)
        self.setObjectName(routeKey)

        self.vBoxLayout.setSpacing(25)
        self.vBoxLayout.setContentsMargins(0, 0, 10, 30)
        self.vBoxLayout.addWidget(self.appCard, 0, Qt.AlignmentFlag.AlignTop)
        #self.vBoxLayout.addWidget(self.galleryCard, 0, Qt.AlignmentFlag.AlignTop)
        self.vBoxLayout.addWidget(self.descriptionCard, 1, Qt.AlignmentFlag.AlignTop)
        self.vBoxLayout.addWidget(self.settingCard, 2, Qt.AlignmentFlag.AlignTop)

        #self.vBoxLayout.addWidget(self.systemCard, 0, Qt.AlignmentFlag.AlignTop)

        self.enableTransparentBackground()

    def showLightBox(self):
        index = self.galleryCard.flipView.currentIndex()
        self.lightBox.setCurrentIndex(index)
        self.lightBox.fadeIn()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.lightBox.resize(self.size())


class NocErrFileDecodeInterface:
    def __init__(self, parent=None, mainWindow=None):
        self.parent = parent
        self.mainWindow = mainWindow
        
        #self.mainWindow.tabBar.currentChanged.connect(self.onTabChanged)
        #self.mainWindow.stackedWidget.setCurrentWidget(self.mainWindow.showInterface)

    def addTab(self, routeKey, text, icon):
        logger.info('[TAB ADD] {}'.format(routeKey))
        self.mainWindow.tabBar.addTab(routeKey, text, icon)

        # tab左对齐
        self.mainWindow.showInterface.addWidget(NocErrFileDecodeCardsInfo(routeKey=routeKey))
        self.mainWindow.showInterface.setCurrentWidget(self.mainWindow.showInterface.findChild(NocErrFileDecodeCardsInfo, routeKey))
        self.mainWindow.stackedWidget.setCurrentWidget(self.mainWindow.showInterface)
        self.mainWindow.tabBar.setCurrentIndex(self.mainWindow.tabBar.count() - 1)
