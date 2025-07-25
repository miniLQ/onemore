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

TZ_SCRIPT_PATH = os.path.join(ROOTPATH, 'tools', 'tz_log_parser')
PYTHON_BIN_ROOT = linuxPath2winPath(os.path.join(ROOTPATH, 'tools', 'Python310'))
PYTHON_BIN_PATH = linuxPath2winPath(os.path.join(ROOTPATH, 'tools', 'Python310', 'python.exe'))
# 获取当前文件的路径
current_path = Path(__file__).resolve().parent
# resource文件夹的路径, 位于当前文件的上两级目录
resource_path = 'app/resource'


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

        self.nameLabel = TitleLabel('TZ Error Code Decode', self)

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
            '快速解析tz_log的一个工具', self)
        self.descriptionLabel.setWordWrap(True)

        self.tagButton = PillPushButton('QCOM', self)
        self.tagButton.setCheckable(False)
        setFont(self.tagButton, 12)
        self.tagButton.setFixedSize(80, 32)

        self.tagButton2 = PillPushButton('TZ', self)
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
        #self.buttonLayout.addWidget(self.shareButton, 0, Qt.AlignmentFlag.AlignRight)

    # def installButtonClicked(self):
    #     if self.installButtonStateTooltip == '已执行':
    #         self.installButtonStateTooltip.setContent('已解析完成')
    #         self.installButtonStateTooltip.setState(True)
    #         self.installButton.setEnabled(True)
    #         self.installButtonStateTooltip = None
    #     else:
    #         self.installButtonStateTooltip = StateToolTip(
    #            '正在解析中', '请耐心等待哦~~', self 
    #         )
    #         # 设置点击后不允许再次点击
    #         self.installButton.setDisabled(True)
    #         # set position 在右下角
    #         self.parent.vBoxLayout.addSpacing(12)
    #         self.parent.vBoxLayout.addWidget(self.installButtonStateTooltip, 3, Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignRight)
            
    #         self.installButtonStateTooltip.show()

class  Worker(QThread):
    signal = pyqtSignal(str)

    def __init__(self, command, shell=True, env=None):
        super().__init__()
        self.command = command
        self.shell = shell
        self.env = env

    def run(self):
        logger.info("Worker Thread ID: {}".format(QThread.currentThreadId()))
        #logger.info("Run command: {}".format(self.command))

        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        if self.shell == True:
            command = "start cmd /K {}".format(self.command)
        else:
            command = self.command
        logger.info("Run command: {}".format(self.command))

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, env=self.env)
        
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
            '这个工具，本软件直接集成(默认集成Strait(O19))。\n但是也支持自定义，手动下载工具放置在软件的tools目录下\n脚本以及错误码路径: \nerrorCodesDict.txt: TZ.XF.5.1.6/trustzone_images/ssg/bsp/qsee/\nprint_tz_log.py: TZ.XF.5.1.6/trustzone_images/ssg/bsp/tz/build/tz/A53_64/RAJAANAA/', self)

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
        self.tzlogfile = ""
        self.outputdir = ""

        # 设置状态提示
        self.stateTooltip = None
        self.bottomStateLayout = QHBoxLayout()

        # 选择按钮以及输入框部件
        self.tzlogfileChooseButton = PushButton("选择")
        #self.fileLineEdit = LineEdit()
        self.outputdirChooseButton = PushButton("选择")

        # 设置Button的点击事件
        self.tzlogfileChooseButton.clicked.connect(self.tzlogfilechooseButtonClicked)
        self.outputdirChooseButton.clicked.connect(self.outputdirButtonClicked)

        # 显示终端部件
        self.comboBox = ComboBox()

        # 设置部件的固定宽度
        self.tzlogfileChooseButton.setFixedWidth(120)
        self.outputdirChooseButton.setFixedWidth(120)

        self.comboBox.setFixedWidth(120)
        self.comboBox.addItems(["始终显示", "始终隐藏"])
        # 设置comboBox的选择点击事件
        self.comboBox.currentIndexChanged.connect(self.comboBoxClicked)

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

        self.tzlogGroup = self.addGroup("{}/images/Rocket.svg".format(resource_path), "tz log file", "选择tz log文件路径", self.tzlogfileChooseButton)
        self.outputGroup = self.addGroup("{}/images/jsdesign.svg".format(resource_path), "输出目录(Optional)", "选择tz log结果的输出目录，默认为tz log file同目录", self.outputdirChooseButton)
        self.addGroup("{}/images/Joystick.svg".format(resource_path), "运行终端", "设置是否显示命令行终端", self.comboBox)
        self.vBoxLayout.addLayout(self.bottomLayout)

        # 设置运行按钮的点击事件
        self.runButton.clicked.connect(self.runButtonClicked)

    def outputdirButtonClicked(self):
        logger.info("Output Choose Button Clicked")
        # 弹出windows文件选择框
        self.outputdir = QFileDialog.getExistingDirectory(self, "选择文件夹")
        # 转成windows路径
        self.outputdir = linuxPath2winPath(self.outputdir)
        # 打印选择的文件路径
        logger.info("Choose Dump Directory: {}".format(self.outputdir))
        
        if self.outputdir == "":
            self.outputdirChooseButton.setText("选择")
            self.outputGroup.setContent("请选择输出目录")
        else:
            # 设置chooseButton的文字显示已选择
            self.outputdirChooseButton.setText("已选择")
            logger.info("path length: {}".format(len(self.outputdir)))
            # 判断self.dumpdir的长度是否大于120
            if len(self.outputdir) > 120:
                # 截取前50个字符和后70个字符
                self.outputGroup.setContent("{}.........{}".format(self.outputdir[0:50], self.outputdir[-70:]))
            else:
                self.outputGroup.setContent(self.outputdir)


    def tzlogfilechooseButtonClicked(self):
        logger.info("tz log input Button Clicked")
        # 弹出windows文件选择框
        self.tzlogfile, _ = QFileDialog.getOpenFileName(self, "选择文件", "C:/", "All Files (*);;Text Files (*.txt)")
        # 转成windows路径
        self.tzlogfile = linuxPath2winPath(self.tzlogfile)
        # 打印选择的文件路径
        logger.info("Choose tz log File: {}".format(self.tzlogfile))

        # # 获取tzlogfile的目录
        # tzlogfile_dir = os.path.dirname(self.tzlogfile)
        # # 设置默认的输出目录为tzlogfile的目录
        # self.outputdir = tzlogfile_dir

        if self.tzlogfile == "":
            # 设置vmlinuxButton的文字显示已选择
            self.tzlogfileChooseButton.setText("选择")
            self.tzlogGroup.setContent("请选择tz log文件")
        else:
            self.tzlogfileChooseButton.setText("已选择")
            # 判断self.vmlinuxfile的长度是否大于150
            logger.info("path length: {}".format(len(self.tzlogfile)))
            if len(self.tzlogfile) > 120:
                # 截取前50个字符和后70个字符
                self.tzlogGroup.setContent("{}.........{}".format(self.tzlogfile[0:50], self.tzlogfile[-70:]))
            else:
                self.tzlogGroup.setContent(self.tzlogfile)

    def comboBoxClicked(self, index):
        logger.info("ComboBox Clicked: {}".format(index))
        # 打印当前选择的值
        logger.info("Current Index: {}".format(self.comboBox.currentText()))

    def showNoSelectFileFlyout(self):
        Flyout.create(
            icon=InfoBarIcon.ERROR,
            title='tz log file is not selected',
            content="请先选择tz log文件",
            target=self.runButton,
            parent=self.window()
        )
    
    def showNoPython(self):
        Flyout.create(
            icon=InfoBarIcon.ERROR,
            title='No python',
            content="请先安装python3环境并添加到环境变量",
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
        os.system("start {}".format(self.outputdir))

    def start_task(self, command, shell):
        logger.info("Start task")
        self.worker = Worker(command, shell=shell)
        self.worker.signal.connect(self.customSignalHandler)
        self.worker.start()

    def runButtonClicked(self):
        logger.info("Run Button Clicked")
        # 获取chooseButton/ vmlinuxButton/ comboBox/ platformComboBox/ lineEdit的值
        logger.info("output directory: {}".format(self.outputdir))
        logger.info("tz log file: {}".format(self.tzlogfile))

        if self.comboBox.currentText() == "始终显示":
            shell = True
        else:
            shell = False

        logger.info("Display terminal: {}".format(shell))

        if self.tzlogfile == "":
            self.showNoSelectFileFlyout()

        else:
            if self.outputdir == "":
                # 获取self.tzlogfile的目录
                tzlogfile_dir = os.path.dirname(self.tzlogfile)
                # 设置默认的输出目录为tzlogfile的目录
                self.outputdir = tzlogfile_dir
                self.outputdirChooseButton.setText("已选择")
                self.outputGroup.setContent("Default Output dir: {}".format(self.outputdir))

            self.stateTooltip = StateToolTip('正在解析', '客官请耐心等待哦~~', self)
            # 状态提示放到中心位置
            self.bottomStateLayout.addWidget(self.stateTooltip, 0, Qt.AlignmentFlag.AlignRight)
            self.vBoxLayout.addLayout(self.bottomStateLayout)
            # 显示状态提示
            self.stateTooltip.show()

            # runbuton按钮设置为不可点击
            self.runButton.setDisabled(True)

            if os.path.exists(self.outputdir) == False:
                os.makedirs(self.outputdir)

            env = os.environ.copy()
            env['PATH'] = os.pathsep.join([os.environ['PATH'], PYTHON_BIN_ROOT])
            env['PATH'] = os.pathsep.join([env['PATH'], os.path.join(PYTHON_BIN_ROOT, 'Scripts')])

            command = '{} {}\\print_tz_log.py -t {} -l {} -o {}'.format(
                        PYTHON_BIN_PATH,
                        TZ_SCRIPT_PATH,
                        TZ_SCRIPT_PATH,
                        self.tzlogfile,
                        os.path.join(self.outputdir, "tz_log_parsed.txt"),)

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

class TzErrorCodeDecodeCardsInfo(ScrollArea):
    """ TzErrorCodeDecode Subinterface """

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


class TzErrorCodeDecodeInterface:
    def __init__(self, parent=None, mainWindow=None):
        self.parent = parent
        self.mainWindow = mainWindow
        self.routeKey = ""

        #self.mainWindow.tabBar.currentChanged.connect(self.onTabChanged)
        #self.mainWindow.stackedWidget.setCurrentWidget(self.mainWindow.showInterface)

    def addTab(self, routeKey, text, icon):
        logger.info('add tab {}'.format(routeKey))
        self.mainWindow.tabBar.addTab(routeKey, text, icon)

        # tab左对齐
        self.mainWindow.showInterface.addWidget(TzErrorCodeDecodeCardsInfo(routeKey=routeKey))
        self.mainWindow.showInterface.setCurrentWidget(self.mainWindow.showInterface.findChild(TzErrorCodeDecodeCardsInfo, routeKey))
        self.mainWindow.stackedWidget.setCurrentWidget(self.mainWindow.showInterface)
        self.mainWindow.tabBar.setCurrentIndex(self.mainWindow.tabBar.count() - 1)

        self.routeKey = routeKey
        logger.info(self.routeKey)
        #logger.info("[LIUQI] CurrentWidget: ".format(self.mainWindow.showInterface.currentWidget()))
        #logger.info("[LIUQI] CurrentWidgetRoutekey: ".format(self.mainWindow.showInterface.currentWidget().objectName()))

    # def onTabChanged(self, index):
    #     objectName = self.mainWindow.tabBar.currentTab().routeKey()
    #     logger.info("[LIUQI1] ObjectName: ", objectName)
    #     logger.info("[LIUQI1] index: ", index)
    #     logger.info("[LIUQI1] CurrentWidget: ", self.mainWindow.showInterface.findChild(LinuxRamdumpParserCardsInfo, objectName))
    #     self.mainWindow.showInterface.setCurrentWidget(self.mainWindow.showInterface.findChild(LinuxRamdumpParserCardsInfo, objectName))
    #     self.mainWindow.stackedWidget.setCurrentWidget(self.mainWindow.showInterface)
    #     self.mainWindow.tabBar.setCurrentIndex(index)
    #     logger.info("[LIUQI1] CurrentWidgetRoutekey: ", self.mainWindow.showInterface.currentWidget().objectName())