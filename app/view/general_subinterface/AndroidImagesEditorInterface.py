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

TOOLS_PATH = os.path.join(ROOTPATH, 'tools')
ANDROID_BOOT_IMAGE_EDITOR_PATH = os.path.join(TOOLS_PATH, "boot_editor")

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

        self.nameLabel = TitleLabel('Android Images Editor', self)

        #self.installButton = PrimaryPushButton('执行', self)
        #self.installButton.clicked.connect(self.installButtonClicked)
        #self.installButtonStateTooltip = None

        #self.companyLabel = HyperlinkLabel(
        #    QUrl('https://qfluentwidgets.com'), 'Shokokawaii Inc.', self)
        self.companyLabel = CaptionLabel('@Designed by cfig.', self)
        #self.installButton.setFixedWidth(160)

        #self.scoreWidget = StatisticsWidget('平均', '5.0', self)
        #self.separator = VerticalSeparator(self)
        #self.commentWidget = StatisticsWidget('评论数', '3K', self)

        self.descriptionLabel = BodyLabel(
            '本工具为github上的开源项目，本人只是将此工具直接集成到onemore中\n作者：cfig\ngithub地址：https://github.com/cfig/Android_boot_image_editor', self)
        self.descriptionLabel.setWordWrap(True)

        self.tagButton = PillPushButton('android', self)
        self.tagButton.setCheckable(False)
        setFont(self.tagButton, 12)
        self.tagButton.setFixedSize(80, 32)

        self.tagButton2 = PillPushButton('unpack', self)
        self.tagButton2.setCheckable(False)
        setFont(self.tagButton2, 12)
        self.tagButton2.setFixedSize(80, 32)

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
        self.buttonLayout.addWidget(self.tagButton2, 1, Qt.AlignmentFlag.AlignLeft)
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
            '本工具为github上的开源项目，本人只是将此工具直接集成到onemore中\n作者：cfig\ngithub地址：https://github.com/cfig/Android_boot_image_editor\n'
            '使用本工具前必须先保证安装好JDK11+的java环境!!!', self)

        self.descriptionLabel.setWordWrap(True)
        self.viewLayout.addWidget(self.descriptionLabel)
        self.setTitle('描述')
        self.setBorderRadius(8)

class SettinsCard(GroupHeaderCardWidget):

    def __init__(self, parent=None, parentvBoxLayout=None):
        super().__init__(parent)
        
        self.output = ""
        self.inputfile = ""

        self.setTitle("基本设置")
        self.setBorderRadius(8)

        # 初始化参数
        self.dumpfile = ""
        self.vmlinuxfile = ""

        # 设置状态提示
        self.stateTooltip = None
        self.bottomStateLayout = QHBoxLayout()

        # 选择按钮以及输入框部件
        self.imagechooseButton = PushButton("选择")
        #self.fileLineEdit = LineEdit()
        self.outputButton = PushButton("选择")

        # 设置Button的点击事件
        self.imagechooseButton.clicked.connect(self.imagechooseButtonClicked)
        self.outputButton.clicked.connect(self.outputButtonClicked)

        # 显示终端部件
        #self.comboBox = ComboBox()
        
        # 平台选择部件
        #self.ComboBox = EditableComboBox()

        # 设置部件的固定宽度
        self.imagechooseButton.setFixedWidth(120)
        self.outputButton.setFixedWidth(120)
        #self.fileLineEdit.setFixedWidth(320)

        # self.comboBox.setFixedWidth(120)
        # self.comboBox.addItems(["始终显示", "始终隐藏"])
        # # 设置comboBox的选择点击事件
        # self.comboBox.currentIndexChanged.connect(self.comboBoxClicked)

        # self.platformComboBox.setPlaceholderText("选择平台")
        # # TODO: 从配置文件中读取平台信息
        # items = ['khaje', 'parrot', 'pitti']
        # self.platformComboBox.setFixedWidth(120)
        # # 设置默认值
        # self.platformComboBox.setCurrentIndex(-1)
    
        # self.platformComboBox.addItems(items)
        # # 设置platformComboBox的编辑事件
        # #self.platformComboBox.currentTextChanged.connect(logger.info)
        # self.platformComboBox.currentIndexChanged.connect(self.platformComboBoxClicked)

        # self.lineEdit.setPlaceholderText("请输入额外的解析参数")

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


        self.inputGroup = self.addGroup("{}/images/Rocket.svg".format(resource_path), "Android image 路径", "请选择image文件", self.imagechooseButton)
        self.outputGroup = self.addGroup("{}/images/jsdesign.svg".format(resource_path), "输出目录", "请选择image unpck的输出目录", self.outputButton)
        #self.addGroup("{}/images/Joystick.svg".format(resource_path), "运行终端", "设置是否显示命令行终端", self.comboBox)
        self.vBoxLayout.addLayout(self.bottomLayout)

        # 设置运行按钮的点击事件
        self.runButton.clicked.connect(self.runButtonClicked)

    def outputButtonClicked(self):
        logger.info("output Choose Button Clicked")
        # 弹出windows文件选择框
        self.output = QFileDialog.getExistingDirectory(self, "选择文件夹")
        # 打印选择的文件路径
        logger.info("Choose output Directory: {}".format(self.output))
        
        if self.output == "":
            self.outputButton.setText("选择")
            self.outputGroup.setContent("请选择output目录")
        else:
            # 设置chooseButton的文字显示已选择
            self.outputButton.setText("已选择")
            self.outputGroup.setContent(self.output)


    def imagechooseButtonClicked(self):
        logger.info("image choose Button Clicked")
        # 弹出windows文件选择框
        self.inputfile, _ = QFileDialog.getOpenFileName(self, "选择文件", "C:/", "All Files (*);;Text Files (*.img)")
        # 打印选择的文件路径
        logger.info("Choose image File: {}".format(self.inputfile))

        if self.inputfile == "":
            # 设置vmlinuxButton的文字显示已选择
            self.imagechooseButton.setText("选择")
            self.inputGroup.setContent("请选择image文件")
        else:
            self.imagechooseButton.setText("已选择")
            self.inputGroup.setContent(self.inputfile)


    def comboBoxClicked(self, index):
        logger.info("ComboBox Clicked: {}".format(index))
        # 打印当前选择的值
        logger.info("Current Index: {}".format(self.comboBox.currentText()))

    # def platformComboBoxClicked(self, index):
    #     logger.info("Platform ComboBox Clicked: ", index)
    #     # 打印当前选择的值
    #     logger.info("Current Index: ", self.platformComboBox.currentText())

    def showNoSelectFileFlyout(self):
        Flyout.create(
            icon=InfoBarIcon.ERROR,
            title='image or output dir is not selected',
            content="请先选择image文件和output目录",
            target=self.runButton,
            parent=self.window()
        )
    
    def showFileStyleErrorFlyout(self):
        Flyout.create(
            icon=InfoBarIcon.ERROR,
            title='image file style error',
            content="需要unpack的镜像应该以.img结尾, 请检查后再执行",
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
        os.system("start {}".format(self.output))


    def start_task(self, command, shell):
        logger.info("Start task")
        self.worker = Worker(command, shell=shell)
        self.worker.signal.connect(self.customSignalHandler)
        self.worker.start()

    def runButtonClicked(self):
        logger.info("Run Button Clicked")
        logger.info("image file path: ".format(self.inputfile))
        logger.info("output directory: ".format(self.output))

        # if self.comboBox.currentText() == "始终显示":
        #     shell = True
        # else:
        #     shell = False

        #logger.info("Display terminal: ", shell)

        if self.output == "" or self.inputfile == "":
            self.showNoSelectFileFlyout()
        # 如果vmlinuxfile的文件名不为vmlinux
        elif not self.inputfile.endswith(".img"):
            # 提示vmlinux文件名不为vmlinux
            self.showFileStyleErrorFlyout()
        else:
            self.stateTooltip = StateToolTip('正在解析', '客官请耐心等待哦~~', self)
            self.bottomStateLayout.addWidget(self.stateTooltip, 0, Qt.AlignmentFlag.AlignRight)
            self.vBoxLayout.addLayout(self.bottomStateLayout)
            # 显示状态提示
            self.stateTooltip.show()

            # runbuton按钮设置为不可点击
            self.runButton.setDisabled(True)

            # command = "cp {} {} && CD {} && {} unpack && cp -r {} {}".format(
            #     self.inputfile, ANDROID_BOOT_IMAGE_EDITOR_PATH, ANDROID_BOOT_IMAGE_EDITOR_PATH, "gradlew.bat",
            #     os.path.join(ANDROID_BOOT_IMAGE_EDITOR_PATH, "build", "unzip_boot"), self.output)
            command = "cp {} {} && CD {} && {} unpack && cp -r {} {} && {} clear".format(
                self.inputfile, ANDROID_BOOT_IMAGE_EDITOR_PATH, ANDROID_BOOT_IMAGE_EDITOR_PATH, "gradlew.bat",
                os.path.join(ANDROID_BOOT_IMAGE_EDITOR_PATH, "build", "unzip_boot"), self.output, "gradlew.bat")
            self.start_task(command, shell=False)
    

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

class AndroidImagesEditorCardsInfo(ScrollArea):
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


class AndroidImagesEditorInterface:
    def __init__(self, parent=None, mainWindow=None):
        self.parent = parent
        self.mainWindow = mainWindow
        
        #self.mainWindow.tabBar.currentChanged.connect(self.onTabChanged)
        #self.mainWindow.stackedWidget.setCurrentWidget(self.mainWindow.showInterface)

    def addTab(self, routeKey, text, icon):
        logger.info('[LIUQI] add tab {} {}'.format(routeKey, text))
        self.mainWindow.tabBar.addTab(routeKey, text, icon)

        # tab左对齐
        self.mainWindow.showInterface.addWidget(AndroidImagesEditorCardsInfo(routeKey=routeKey))
        self.mainWindow.showInterface.setCurrentWidget(self.mainWindow.showInterface.findChild(AndroidImagesEditorCardsInfo, routeKey))
        self.mainWindow.stackedWidget.setCurrentWidget(self.mainWindow.showInterface)
        self.mainWindow.tabBar.setCurrentIndex(self.mainWindow.tabBar.count() - 1)

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