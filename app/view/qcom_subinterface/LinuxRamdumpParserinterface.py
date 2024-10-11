from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from qfluentwidgets import CardWidget
import sys
from pathlib import Path
import os

import time

from PyQt6.QtCore import Qt, QPoint, QSize, QUrl, QRect, QPropertyAnimation
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

from code.sadp import run_parse
from app.common.config import ROOTPATH
import asyncio

GNU_TOOLS_PATH = os.path.join(ROOTPATH, 'tools', 'gnu-tools')

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

        self.nameLabel = TitleLabel('Linux Ramdump Parser', self)

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
            'Linux Ramdump Parser 是高通平台开发提供给研发人员进行Ramdump的解析使用的一个工具', self)
        self.descriptionLabel.setWordWrap(True)

        self.tagButton = PillPushButton('QCOM', self)
        self.tagButton.setCheckable(False)
        setFont(self.tagButton, 12)
        self.tagButton.setFixedSize(80, 32)

        self.tagButton2 = PillPushButton('Ramdump', self)
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

class DescriptionCard(HeaderCardWidget):
    """ Description card """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.descriptionLabel = BodyLabel(
            'Linux Ramdump Parser 是高通平台开发提供给研发人员进行Ramdump的解析使用的一个工具。本软件暂时不直接集成，需手动下载工具放置在软件的tools目录下', self)

        self.descriptionLabel.setWordWrap(True)
        self.viewLayout.addWidget(self.descriptionLabel)
        self.setTitle('描述')
        self.setBorderRadius(8)

class SettinsCard(GroupHeaderCardWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("基本设置")
        self.setBorderRadius(8)

        # 初始化参数
        self.dumpfile = ""
        self.vmlinuxfile = ""

        # 设置状态提示
        #self.stateTooltip = None

        # 选择按钮以及输入框部件
        self.chooseButton = PushButton("选择")
        #self.fileLineEdit = LineEdit()
        self.vmlinuxButton = PushButton("选择")

        # 设置Button的点击事件
        self.chooseButton.clicked.connect(self.chooseButtonClicked)
        self.vmlinuxButton.clicked.connect(self.vmlinuxButtonClicked)

        # 显示终端部件
        #self.comboBox = ComboBox()
        
        # 平台选择部件
        self.platformComboBox = EditableComboBox()

        # 入口脚本部件
        self.lineEdit = LineEdit()

        # 设置部件的固定宽度
        self.chooseButton.setFixedWidth(120)
        self.vmlinuxButton.setFixedWidth(120)
        #self.fileLineEdit.setFixedWidth(320)

        self.lineEdit.setFixedWidth(320)
        #self.comboBox.setFixedWidth(120)
        #self.comboBox.addItems(["始终显示", "始终隐藏"])
        # 设置comboBox的选择点击事件
        #self.comboBox.currentIndexChanged.connect(self.comboBoxClicked)

        self.platformComboBox.setPlaceholderText("选择平台")
        # TODO: 从配置文件中读取平台信息
        items = ['khaje', 'parrot', 'pitti']
        self.platformComboBox.setFixedWidth(120)
        # 设置默认值
        self.platformComboBox.setCurrentIndex(-1)
    
        self.platformComboBox.addItems(items)
        # 设置platformComboBox的编辑事件
        #self.platformComboBox.currentTextChanged.connect(print)
        self.platformComboBox.currentIndexChanged.connect(self.platformComboBoxClicked)

        self.lineEdit.setPlaceholderText("请输入额外的解析参数")

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


        self.ramdumpGroup = self.addGroup("{}/images/Rocket.svg".format(resource_path), "Ramdump目录", "选择Ramdump的存放目录", self.chooseButton)
        self.vmlinuxGroup = self.addGroup("{}/images/jsdesign.svg".format(resource_path), "vmlinux文件", "选择vmlinux文件路径", self.vmlinuxButton)
        self.addGroup("{}/images/Joystick.svg".format(resource_path), "Platform", "选择基线平台", self.platformComboBox)
        #self.addGroup("{}/images/Joystick.svg".format(resource_path), "运行终端", "设置是否显示命令行终端", self.comboBox)
        self.addGroup("{}/images/Python.svg".format(resource_path), "额外参数", "请输入额外的解析参数", self.lineEdit)
        self.vBoxLayout.addLayout(self.bottomLayout)

        # 设置运行按钮的点击事件
        self.runButton.clicked.connect(self.runButtonClicked)

    def chooseButtonClicked(self):
        print("Choose Button Clicked")
        # 弹出windows文件选择框
        self.dumpdir = QFileDialog.getExistingDirectory(self, "选择文件夹")
        # 打印选择的文件路径
        print("Choose Dump Directory: ", self.dumpdir)
        
        if self.dumpdir == "":
            self.chooseButton.setText("选择")
        else:
            # 设置chooseButton的文字显示已选择
            self.chooseButton.setText("已选择")

        # 更新lineEdit的内容
        self.ramdumpGroup.setContent(self.dumpdir)


    def vmlinuxButtonClicked(self):
        print("vmlinux Button Clicked")
        # 弹出windows文件选择框
        self.vmlinuxfile, _ = QFileDialog.getOpenFileName(self, "选择文件", "C:/", "All Files (*);;Text Files (*.txt)")
        # 打印选择的文件路径
        print("Choose Vmlinux File: ", self.vmlinuxfile)

        if self.vmlinuxfile == "":
            # 设置vmlinuxButton的文字显示已选择
            self.vmlinuxButton.setText("选择")
        else:
            self.vmlinuxButton.setText("已选择")
        
        # 更新lineEdit的内容
        self.vmlinuxGroup.setContent(self.vmlinuxfile)

    def comboBoxClicked(self, index):
        print("ComboBox Clicked: ", index)
        # 打印当前选择的值
        print("Current Index: ", self.comboBox.currentText())

    def platformComboBoxClicked(self, index):
        print("Platform ComboBox Clicked: ", index)
        # 打印当前选择的值
        print("Current Index: ", self.platformComboBox.currentText())

    def showNoSelectFileFlyout(self):
        Flyout.create(
            icon=InfoBarIcon.ERROR,
            title='Vmlinux or Dump file is not selected',
            content="请先选择vmlinux文件和dump文件",
            target=self.runButton,
            parent=self.window()
        )
    
    def showFileStyleErrorFlyout(self):
        Flyout.create(
            icon=InfoBarIcon.ERROR,
            title='Vmlinux file style error',
            content="vmlinux文件名不为vmlinux, 请检查后再执行",
            target=self.runButton,
            parent=self.window()
        )

    def showZipFileTypeErrorFlyout(self):
        Flyout.create(
            icon=InfoBarIcon.ERROR,
            title='Dump file type error',
            content="压缩包请先行解压，请检查后再执行",
            target=self.runButton,
            parent=self.window()
        )

    async def run_process(self, command, shell):
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                print(f"{line.decode().strip()}")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await process.wait()
            print(f"Process return code: {process.returncode}")

    def runButtonClicked(self):
        print("Run Button Clicked")
        # 获取chooseButton/ vmlinuxButton/ comboBox/ platformComboBox/ lineEdit的值
        print("Dump directory: ", self.dumpdir)
        print("Vmlinux file: ", self.vmlinuxfile)
        print("platform: ", self.platformComboBox.currentText())
        print("extend parameters: ", self.lineEdit.text())
        #print("Display terminal: ", self.comboBox.currentText())

        # if self.comboBox.currentText() == "始终显示":
        #     print("Display terminal")
        #     shell = True
        # else:
        #     shell = False

        if self.dumpdir == "" or self.vmlinuxfile == "":
            self.showNoSelectFileFlyout()
        # elif self.dumpfile.endswith('.zip') == True or self.dumpfile.endswith('.rar') == True:
        #     self.showZipFileTypeErrorFlyout()
        # 如果vmlinuxfile的文件名不为vmlinux
        elif os.path.basename(self.vmlinuxfile) != "vmlinux":
            # 提示vmlinux文件名不为vmlinux
            self.showFileStyleErrorFlyout()
        else:
            # self.stateTooltip = StateToolTip('正在解析', '客官请耐心等待哦~~', self)
            # self.stateTooltip.move(700, 20)
            # self.stateTooltip.show()

            # runbuton按钮设置为不可点击
            # self.runButton.setDisabled(True)

            time.sleep(3)

            # TODO: 执行解析命令
            #p = run_parse(dumpdir=self.dumpdir, vmlinuxfile=self.vmlinuxfile, platform=self.platformComboBox.currentText(), extendParams=self.lineEdit.text(), shell=shell)
            ramdump_parse_tool_path = os.path.join(ROOTPATH, 'tools', 'linux-ramdump-parser-v2')
            gdb64_path = os.path.join(GNU_TOOLS_PATH, 'bin', 'gdb.exe')
            nm64_path = os.path.join(GNU_TOOLS_PATH, 'bin', 'aarch64-linux-gnu-nm.exe')
            objdump64_path = os.path.join(GNU_TOOLS_PATH, 'bin', 'aarch64-linux-gnu-objdump.exe')
            output_path = os.path.join(self.dumpdir, 'parser_output')

            command = 'python {}\\ramparse.py -v {} -g {} -n {} -j {} -a {} -o {} --force-hardware {} -x {}'.format(ramdump_parse_tool_path,
                    self.vmlinuxfile, gdb64_path, nm64_path, objdump64_path, self.dumpdir, output_path, self.platformComboBox.currentText(), self.lineEdit.text())

            print(f"Run parse with command: {command}")
            
            os.system("start cmd.exe /K {}".format(command))

            #asyncio.run(self.run_process(command, shell))

        print("Run Button Finished")
        # self.stateTooltip.setContent('解析完成')
        # self.stateTooltip.setState(True)
        # self.runButton.setEnabled(True)
        # self.stateTooltip.show()


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

class LinuxRamdumpParserCardsInfo(ScrollArea):
    """ Linux Ramdump Parser Subinterface """

    def __init__(self, parent=None, routeKey=None):
        super().__init__(parent=parent)

        self.view = QWidget(self)

        self.routeKey = routeKey

        self.vBoxLayout = QVBoxLayout(self.view)
        self.appCard = AppInfoCard(parent=self)
        #self.galleryCard = GalleryCard(self)
        self.descriptionCard = DescriptionCard(self)
        self.settingCard = SettinsCard(self)
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


class LinuxRamdumpParserInterface:
    def __init__(self, parent=None, mainWindow=None):
        self.parent = parent
        self.mainWindow = mainWindow
        
        #self.mainWindow.tabBar.currentChanged.connect(self.onTabChanged)
        #self.mainWindow.stackedWidget.setCurrentWidget(self.mainWindow.homeInterface)

    def addTab(self, routeKey, text, icon):
        print(f'[LIUQI] add tab {routeKey} {text} {icon}')
        self.mainWindow.tabBar.addTab(routeKey, text, icon)

        # tab左对齐
        self.mainWindow.homeInterface.addWidget(LinuxRamdumpParserCardsInfo(routeKey=routeKey))
        self.mainWindow.homeInterface.setCurrentWidget(self.mainWindow.homeInterface.findChild(LinuxRamdumpParserCardsInfo, routeKey))
        self.mainWindow.stackedWidget.setCurrentWidget(self.mainWindow.homeInterface)
        self.mainWindow.tabBar.setCurrentIndex(self.mainWindow.tabBar.count() - 1)

        print("[LIUQI] CurrentWidget: ", self.mainWindow.homeInterface.currentWidget())
        print("[LIUQI] CurrentWidgetRoutekey: ", self.mainWindow.homeInterface.currentWidget().objectName())

    # def onTabChanged(self, index):
    #     objectName = self.mainWindow.tabBar.currentTab().routeKey()
    #     print("[LIUQI1] ObjectName: ", objectName)
    #     print("[LIUQI1] index: ", index)
    #     print("[LIUQI1] CurrentWidget: ", self.mainWindow.homeInterface.findChild(LinuxRamdumpParserCardsInfo, objectName))
    #     self.mainWindow.homeInterface.setCurrentWidget(self.mainWindow.homeInterface.findChild(LinuxRamdumpParserCardsInfo, objectName))
    #     self.mainWindow.stackedWidget.setCurrentWidget(self.mainWindow.homeInterface)
    #     self.mainWindow.tabBar.setCurrentIndex(index)
    #     print("[LIUQI1] CurrentWidgetRoutekey: ", self.mainWindow.homeInterface.currentWidget().objectName())