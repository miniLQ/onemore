from PyQt6.QtCore import Qt, QThread
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from qfluentwidgets import CardWidget
import sys
from pathlib import Path
import os
import subprocess

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

TOOLS_PATH = os.path.join(ROOTPATH, 'tools')

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
        self.iconLabel = ImageLabel("{}/images/Rocket.svg".format(resource_path), self)
        self.iconLabel.setBorderRadius(8, 8, 8, 8)
        self.iconLabel.scaledToWidth(120)

        self.nameLabel = TitleLabel('Memory Analyzer tool', self)

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
            'Memory Analyzer Tool，简称MAT', self)
        self.descriptionLabel.setWordWrap(True)

        self.tagButton = PillPushButton('gdb', self)
        self.tagButton.setCheckable(False)
        setFont(self.tagButton, 12)
        self.tagButton.setFixedSize(80, 32)

        # self.tagButton2 = PillPushButton('gdb', self)
        # self.tagButton2.setCheckable(False)
        # setFont(self.tagButton2, 12)
        # self.tagButton2.setFixedSize(80, 32)

        # self.tagButton3 = PillPushButton('pack', self)
        # self.tagButton3.setCheckable(False)
        # setFont(self.tagButton3, 12)
        # self.tagButton3.setFixedSize(80, 32)

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
        #self.buttonLayout.addWidget(self.tagButton2, 1, Qt.AlignmentFlag.AlignLeft)
        #self.buttonLayout.addWidget(self.shareButton, 0, Qt.AlignmentFlag.AlignRight)


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
            'MAT是一款快速便捷且功能强大丰富的 JVM 堆内存离线分析工具。其通过展现 JVM 异常时所记录的运行时堆转储快照（Heap dump）状态（正常运行时也可以做堆转储分析），帮助定位内存泄漏问题或优化大内存消耗逻辑\n'
            '如果工具解析报错An internal error occurred during: "Parsing heap dump from"\n'
            '请打开软件目录/tools/mat/MemoryAnalyzer.ini\n'
            '修改第七行中1024为5120（此值需要大于hprof文件大小）', self)

        self.descriptionLabel.setWordWrap(True)
        self.viewLayout.addWidget(self.descriptionLabel)
        self.setTitle('描述')
        self.setBorderRadius(8)

class SettinsCard(GroupHeaderCardWidget):

    def __init__(self, parent=None, parentvBoxLayout=None):
        super().__init__(parent)
        

        self.setTitle("基本设置")
        self.setBorderRadius(8)

        # 初始化参数
        self.hproffile = ""
        self.translate = False

        # 设置状态提示
        self.stateTooltip = None
        self.bottomStateLayout = QHBoxLayout()

        # 选择按钮以及输入框部件
        self.hproffileButton = PushButton("选择")
        #self.fileLineEdit = LineEdit()


        # 设置Button的点击事件
        self.hproffileButton.clicked.connect(self.hproffilechooseButtonClicked)

        # 设置部件的固定宽度
        self.hproffileButton.setFixedWidth(120)

                # 显示终端部件
        self.comboBox = ComboBox()

        self.comboBox.setFixedWidth(120)
        self.comboBox.addItems(["Yes", "No"])
        # 设置comboBox的选择点击事件
        self.comboBox.currentIndexChanged.connect(self.comboBoxClicked)
        self.comboBox.setCurrentIndex(-1)

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


        self.hproffileGroup = self.addGroup("{}/images/Rocket.svg".format(resource_path), "hprof文件路径", "请选择文件", self.hproffileButton)
        self.addGroup("{}/images/jsdesign.svg".format(resource_path), "hprof是否需要转换", "请选择", self.comboBox)
 
        self.vBoxLayout.addLayout(self.bottomLayout)

        # 设置运行按钮的点击事件
        self.runButton.clicked.connect(self.runButtonClicked)

    def hproffilechooseButtonClicked(self):
        logger.info("hprof choose Button Clicked")
        # 弹出windows文件选择框
        self.hproffile, _ = QFileDialog.getOpenFileName(self, "选择文件", "C:/", "All Files (*);;Text Files (*.img)")
        # self.hproffile转换成windows路径
        self.hproffile = linuxPath2winPath(self.hproffile)
        # 打印选择的文件路径
        logger.info("Choose hprof File: {}".format(self.hproffile))

        
        if self.hproffile == "":
            self.hproffileButton.setText("选择")
            self.hproffileGroup.setContent("请选择output目录")
        else:
            # 设置chooseButton的文字显示已选择
            self.hproffileButton.setText("已选择")
            self.hproffileGroup.setContent(self.hproffile)


    def comboBoxClicked(self, index):
        logger.info("ComboBox Clicked")
        logger.info("Current Index: {}".format(self.comboBox.currentText()))

        if self.comboBox.currentText() == "Yes":
            self.translate = True
        else:
            self.translate = False

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
        #os.system("start {}".format(self.output))


    def start_task(self, command, shell):
        logger.info("Start task")
        self.worker = Worker(command, shell=shell)
        self.worker.signal.connect(self.customSignalHandler)
        self.worker.start()

    def runButtonClicked(self):
        logger.info("Run Button Clicked")
        logger.info("hprof file path: {}".format(self.hproffile))

        if self.hproffile == "":
            self.showNoSelectFileFlyout()
            return
        
        if self.comboBox.currentText() == "":
            self.showNoSelectParamFlyout()
            return
        
        self.stateTooltip = StateToolTip('正在解析', '客官请耐心等待哦~~', self)
        self.bottomStateLayout.addWidget(self.stateTooltip, 0, Qt.AlignmentFlag.AlignRight)
        self.vBoxLayout.addLayout(self.bottomStateLayout)
        # 显示状态提示
        self.stateTooltip.show()

        # runbuton按钮设置为不可点击
        self.runButton.setDisabled(True)

        #command = "CD /d {} && start startGDB.bat {} {}".format(GDBTOOL_PATH, self.executablefile, self.coredumpfile)

        if self.translate == True:
            newfile = "output.hprof"
            # 获取self.hproffile的路径
            path = os.path.dirname(self.hproffile)
            command = "{} {} {}".format(linuxPath2winPath(os.path.join(TOOLS_PATH, "android-sdk", "lib", "hprof-conv.exe")), self.hproffile, linuxPath2winPath(os.path.join(path, newfile)))
            logger.info(command)
            os.system(command)

            command = "{} {}".format(linuxPath2winPath(os.path.join(TOOLS_PATH, "mat", "MemoryAnalyzer.exe")), linuxPath2winPath(os.path.join(path, newfile)))
            logger.info(command)
            self.start_task(command, shell=False)
        else:
            command = "{} {}".format(linuxPath2winPath(os.path.join(TOOLS_PATH, "mat", "MemoryAnalyzer.exe")), self.hproffile)
            logger.info(command)
            self.start_task(command, shell=False)


    def showNoSelectFileFlyout(self):
        Flyout.create(
            icon=InfoBarIcon.ERROR,
            title='hprof文件未选择',
            content="请先选择需要解析的hprof文件",
            target=self.runButton,
            parent=self.window()
        )
    
    def showNoSelectParamFlyout(self):
        Flyout.create(
            icon=InfoBarIcon.ERROR,
            title='hprof是否需要转换未选择',
            content="请选择是否需要转换hprof文件",
            target=self.runButton,
            parent=self.window()
        )

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

class MatCardsInfo(ScrollArea):
    """ MAT Subinterface """

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


class MatInterface:
    def __init__(self, parent=None, mainWindow=None):
        self.parent = parent
        self.mainWindow = mainWindow
        
        #self.mainWindow.tabBar.currentChanged.connect(self.onTabChanged)
        #self.mainWindow.stackedWidget.setCurrentWidget(self.mainWindow.showInterface)

    def addTab(self, routeKey, text, icon):
        logger.info('[TAB ADD] {}'.format(routeKey))
        self.mainWindow.tabBar.addTab(routeKey, text, icon)

        # tab左对齐
        self.mainWindow.showInterface.addWidget(MatCardsInfo(routeKey=routeKey))
        self.mainWindow.showInterface.setCurrentWidget(self.mainWindow.showInterface.findChild(MatCardsInfo, routeKey))
        self.mainWindow.stackedWidget.setCurrentWidget(self.mainWindow.showInterface)
        self.mainWindow.tabBar.setCurrentIndex(self.mainWindow.tabBar.count() - 1)
