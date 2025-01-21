from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from qfluentwidgets import CardWidget
import sys
from pathlib import Path
import os
import subprocess
from datetime import datetime
import time
import re

from PyQt6.QtCore import Qt, QPoint, QSize, QUrl, QRect, QPropertyAnimation, pyqtSignal, QObject
from PyQt6.QtGui import QIcon, QFont, QColor, QPainter
from PyQt6.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QGraphicsOpacityEffect, QFileDialog, QMessageBox

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
LLVMTOOL_PATH = os.path.join(TOOLS_PATH, "android-sdk", "bin")

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
        self.iconLabel = ImageLabel("{}/images/Basketball.png".format(resource_path), self)
        self.iconLabel.setBorderRadius(8, 8, 8, 8)
        self.iconLabel.scaledToWidth(120)

        self.nameLabel = TitleLabel('Tombstone_Praser', self)
        self.companyLabel = CaptionLabel('@Designed by charter.', self)
        self.descriptionLabel = BodyLabel(
            'Tombstone_Praser tool 是基于add2line工具集成的用于解析带有堆栈的crash log的通用工具', self)
        self.descriptionLabel.setWordWrap(True)

        self.tagButton = PillPushButton('addr2line', self)
        self.tagButton.setCheckable(False)
        setFont(self.tagButton, 12)
        self.tagButton.setFixedSize(80, 32)

        self.tagButton2 = PillPushButton('Tombstone', self)
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

class DescriptionCard(HeaderCardWidget):
    """ Description card """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.descriptionLabel = BodyLabel(
            'Tombstone_Praser tool 是基于add2line工具集成的用于解析带有堆栈的crash log的通用工具。本软件内直接集成LLVM工具包，无需下载，直接选择symbols目录，再选择tombstone文件或目录进行解析即可！\n 解析步骤：\n'
            '1. 选择带有符号表的symbols目录\n'
            '2. 选择需要解析的tombstone文件或目录\n'
            '3. 执行\n'
            '4. 执行结束后，结果文件以“tombstone文件名+parser_result”命名\n'
            '提示：解析的结果生成在同tombstone目录下', self)

        self.descriptionLabel.setWordWrap(True)
        self.viewLayout.addWidget(self.descriptionLabel)
        self.setTitle('描述')
        self.setBorderRadius(8)

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
            command = "start cmd /c {}".format(self.command)
        else:
            command = self.command
        
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        
        while True:
            line = process.stdout.readline()
            if not line:
                break
            logger.info(line.decode('gbk').strip())

        self.signal.emit("SUCCESS")

class SettinsCard(GroupHeaderCardWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("基本设置")
        self.setBorderRadius(8)

        self.symbolsdir = ""
        self.tombstonefile = ""
        self.tombstonedir = ""

        self.tombstone = ""
        self.vendor_version = "t"
        self.result_message = "" 

        # 选择按钮以及输入框部件
        self.symbolschooseButton = PushButton("选择")
        self.tombstonefilechooseButton = PushButton("选择")
        self.tombstonedirchooseButton = PushButton("选择")

        # 显示终端部件
        #self.comboBox = ComboBox()
        # 显示tombstone类型部件
        self.tombstonecomboBox = ComboBox()
        self.vendorcomboBox = ComboBox()

        # 入口脚本部件
        #self.lineEdit = LineEdit()

        # 设置部件的固定宽度
        self.symbolschooseButton.setFixedWidth(120)
        self.tombstonefilechooseButton.setFixedWidth(120)
        self.tombstonedirchooseButton.setFixedWidth(120)

        # self.comboBox.setFixedWidth(320)
        # self.comboBox.addItems(["始终显示", "始终隐藏"])
        #选择文件/选择目录
        self.tombstonecomboBox.setFixedWidth(320)
        self.tombstonecomboBox.addItems(["选择文件", "选择目录"])
        self.tombstonedirchooseButton.setEnabled(False)
        self.tombstonecomboBox.currentIndexChanged.connect(self.on_combobox_changed)
        #选择vendor版本
        self.vendorcomboBox.setFixedWidth(320)
        self.vendorcomboBox.addItems(["S", "T", "U", "V"])
        self.vendorcomboBox.setCurrentText("T")
        self.vendorcomboBox.currentIndexChanged.connect(self.on_vendorcombobox_changed)

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

        # 设置状态提示
        self.stateTooltip = None
        self.bottomStateLayout = QHBoxLayout()
        
        # 设置底部状态布局
        self.bottomStateLayout.setSpacing(10)
        self.bottomStateLayout.setContentsMargins(24, 15, 24, 20)
        self.bottomStateLayout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.bottomStateLayout.addStretch(1)
        #symbols目录（请选择目录）                                  选择
        #tombstone类型（请选择需要解析单个文件还是整个目录下的文件）  （选择文件/选择目录）
        #tombstone文件（请选择文件）                                选择
        #tombstone目录（请选择目录）                                选择
        #vendor版本（请选择vendor版本）                             （S/T/U/V）
        self.symbolsgroup = self.addGroup("{}/images/Basketball.png".format(resource_path), "symbols目录", "请选择目录", self.symbolschooseButton)
        self.addGroup("{}/images/Basketball.png".format(resource_path), "tombstone类型", "请选择需要解析单个文件还是整个目录下的文件", self.tombstonecomboBox)
        self.tombstonefilegroup = self.addGroup("{}/images/Basketball.png".format(resource_path), "tombstone文件", "请选择文件", self.tombstonefilechooseButton)
        self.tombstonedirgroup = self.addGroup("{}/images/Basketball.png".format(resource_path), "tombstone目录", "请选择目录", self.tombstonedirchooseButton)
        self.addGroup("{}/images/Basketball.png".format(resource_path), "vendor版本", "请选择vendor版本", self.vendorcomboBox)
        self.vBoxLayout.addLayout(self.bottomLayout)

        self.symbolschooseButton.clicked.connect(self.onsymbolsChooseButtonClicked)
        self.tombstonefilechooseButton.clicked.connect(self.ontombstonefileChooseButtonClicked)
        self.tombstonedirchooseButton.clicked.connect(self.ontombstonedirChooseButtonClicked)
        self.runButton.clicked.connect(self.onRunButtonClicked)

    #选择目录/选择文件
    def on_combobox_changed(self, index):
        if index > 0:
            self.tombstonefilechooseButton.setEnabled(False)
            self.tombstonedirchooseButton.setEnabled(True)
        else:
            self.tombstonedirchooseButton.setEnabled(False)
            self.tombstonefilechooseButton.setEnabled(True)
    #选择vendor版本
    def on_vendorcombobox_changed(self, index):
        if index > 0:
            self.vendor_version = "t"
        else:
            self.vendor_version = "s"

    #错误提示
    def showFileStyleErrorFlyout(self):
        Flyout.create(
            icon=InfoBarIcon.ERROR,
            title='目录选择错误',
            content="需要带有符号表的symbols, 请检查后再执行",
            target=self.runButton,
            parent=self.window()
        )
    def showNofileErrorFlyout(self):
        Flyout.create(
            icon=InfoBarIcon.ERROR,
            title='dir is not choose',
            content="目录未选择, 请检查后再执行",
            target=self.runButton,
            parent=self.window()
        )

    #symbols目录选择事件
    def onsymbolsChooseButtonClicked(self):
        logger.info("symbols Choose Button Clicked!")
        self.symbolsdir = QFileDialog.getExistingDirectory(self, "选择文件夹")
        # 转换为windows路径
        self.symbolsdir = linuxPath2winPath(self.symbolsdir)
        logger.info("symbols dir: {}".format(self.symbolsdir))

        if self.symbolsdir == "":
            self.symbolschooseButton.setText("选择")
            self.symbolsgroup.setContent("请选择目录")
        else:
            self.symbolschooseButton.setText("已选择")
            self.symbolsgroup.setContent(self.symbolsdir)
    #tombstone文件选择事件
    def ontombstonefileChooseButtonClicked(self):
        logger.info("tombstonefile choose Button Clicked")
        # 弹出windows文件选择框
        self.tombstonefile, _ = QFileDialog.getOpenFileName(self, "选择文件", "C:/", "All Files (*);")
        # 转化为windows路径
        self.tombstonefile = linuxPath2winPath(self.tombstonefile)
        # 打印选择的文件路径
        logger.info("Choose executable File: {}".format(self.tombstonefile))

        if self.tombstonefile == "":
            # 设置vmlinuxButton的文字显示已选择
            self.tombstonefilechooseButton.setText("选择")
            self.tombstonefilegroup.setContent("请选择log文件")
        else:
            self.tombstonefilechooseButton.setText("已选择")
            self.tombstonefilegroup.setContent(self.tombstonefile)
            self.tombstone = self.tombstonefile
    #tombstone目录选择事件
    def ontombstonedirChooseButtonClicked(self):
        logger.info("tombstonedir choose Button Clicked")
        self.tombstonedir = QFileDialog.getExistingDirectory(self, "选择文件夹")
        # 转换为windows路径
        self.tombstonedir = linuxPath2winPath(self.tombstonedir)
        logger.info("tombstone dir: {}".format(self.tombstonedir))

        if self.tombstonedir == "":
            self.tombstonedirchooseButton.setText("选择")
            self.tombstonedirgroup.setContent("请选择目录")
        else:
            self.tombstonedirchooseButton.setText("已选择")
            self.tombstonedirgroup.setContent(self.tombstonedir)
            self.tombstone = self.tombstonedir

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

        # 打开解析完成的文件夹
        logger.info("output dir: {}".format(self.symbolsdir))
        os.system("start {}".format(self.symbolsdir))

    #unuse
    def start_task(self, command, shell):
        logger.info("Start task")
        self.worker = Worker(command, shell=shell)
        self.worker.signal.connect(self.customSignalHandler)
        self.worker.start()
    #运行事件
    def onRunButtonClicked(self):
        logger.info("run button clicked!")

        if self.symbolsdir == "":
            self.showNofileErrorFlyout()
        else:
            self.stateTooltip = StateToolTip('正在解析', '客官请耐心等待哦~~', self)
            # 状态提示放到中心位置
            self.bottomStateLayout.addWidget(self.stateTooltip, 0, Qt.AlignmentFlag.AlignRight)
            self.vBoxLayout.addLayout(self.bottomStateLayout)
            # 显示状态提示
            self.stateTooltip.show()

            # runbuton按钮设置为不可点击
            self.runButton.setDisabled(True)

            # if self.comboBox.currentText() == "始终显示":
            #     shell = True
            # else:
            #     shell = False
    
            # if self.tombstonefile != "":
            #     command = "{} -a -i -Cfe {} {}".format(linuxPath2winPath(os.path.join(LLVMTOOL_PATH, "llvm-addr2line.exe")), self.symbolsdir, self.tombstonefile)

            # self.start_task(command, shell)
            self.result_message = start_parse(self.symbolsdir, self.tombstone, LLVMTOOL_PATH, self.vendor_version)

            if self.result_message != "":
                if os.path.isdir(self.tombstone):
                        try:
                            subprocess.run(["explorer", self.tombstone])
                        except Exception as e:
                            QMessageBox.warning(self, "错误", f"打开文件夹时发生错误: {e}")
                else:
                    directory = os.path.dirname(self.tombstone)
                    if os.path.isdir(directory):
                        try:
                            subprocess.run(["explorer", directory])
                        except Exception as e:
                            QMessageBox.warning(self, "错误", f"打开文件夹时发生错误: {e}")
                self.stateTooltip.close()
                self.stateTooltip2 = StateToolTip('解析完成', '为您打开生成目录~~', self)
                self.bottomStateLayout.addWidget(self.stateTooltip2, 0, Qt.AlignmentFlag.AlignRight)
                self.stateTooltip2.show()
                self.runButton.setDisabled(False)
            else:
                self.stateTooltip.close()
                self.stateTooltip2 = StateToolTip('错误', '结果不存在！', self)
                self.bottomStateLayout.addWidget(self.stateTooltip2, 0, Qt.AlignmentFlag.AlignRight)
                self.stateTooltip2.show()
                self.runButton.setDisabled(False)

#解析单个文件
def parse_single_tomb(symbols_path, tomb_path, tools_dir, vendor_version):
    result_name = os.path.join(os.path.dirname(tomb_path), os.path.basename(tomb_path) + "_parser_result.txt")
    with open(tomb_path, 'r', encoding='utf-8') as fp, open(result_name, "w+") as f_result:
        for line in fp:
            rst_common = re.search(r'(#[0-9]{2})\s+pc\s+([0-9a-z]*)\s+(.+?)\s+', line)
            rst_asan = re.search(r'(#[0-9]{1,2}).+\((.+?)\+([0-9a-z]*)\)', line)

            so_path, address = "", ""
            if rst_common:
                so_path, address = rst_common.group(3), rst_common.group(2)
            elif rst_asan:
                so_path, address = rst_asan.group(2), rst_asan.group(3)

            if so_path and address:
                analysis_result = tomba_so(symbols_path, so_path, address, tools_dir, vendor_version)
                f_result.write(line)
                f_result.write(analysis_result)
                f_result.write("\n")
            else:
                f_result.write(line)
    return result_name
#解析目录下所有文件
def parse_tomb_directory(symbols_path, tomb_dir, tools_dir, vendor_version):

    result_files = []
    for root, _, files in os.walk(tomb_dir):
        for file in files:
            tomb_path = os.path.join(root, file)
            result_file = parse_single_tomb(symbols_path, tomb_path, tools_dir, vendor_version)
            result_files.append(result_file)
    return result_files

#获取解析工具路径
def get_tool_path(tool_name, tools_dir):
    return os.path.join(tools_dir, tool_name)

#addr2line解析so
def tomba_so(symbols_path, so_path, address, tools_dir, vendor_version):
    so_full_path = os.path.join(symbols_path, so_path.lstrip('/'))
    if os.path.exists(so_full_path):
        tool = "llvm-addr2line.exe" if vendor_version != 's' else "addr2line" #Vendor的s版本及以下使用addr2line
        tool_path = get_tool_path(tool, tools_dir)
        cmd_line = f"{tool_path} -a -i -Cfe {so_full_path} {address}"
        result = os.popen(cmd_line).read()
        return result
    else:
        # logger.info(f"[Error] {so_path} not found in symbols ({symbols_path})")
        return f"[Error] {so_path} not found in symbols ({symbols_path})"  

def start_parse(symbols_system, tombstone_file, parse_backtrace_tools_dir, version):
    start_time = time.time()
    logger.info("Starting parse...")

    if os.path.isdir(tombstone_file): #判断是否为文件夹
        result_files = parse_tomb_directory(
            symbols_system, tombstone_file, parse_backtrace_tools_dir, version
        )
        result_message = "\n".join(result_files)
    else:
        result_file = parse_single_tomb(
            symbols_system, tombstone_file, parse_backtrace_tools_dir, version
        )
        result_message = result_file

    end_time = time.time()
    logger.info(f"Parse completed!\nResults:\n{result_message}\nTime: {end_time - start_time:.2f}s")
    #print(f"Parse backtrace completed. Total time: {end_time - start_time:.2f}s")
    #messagebox.showinfo("Completed", f"Parse completed!\nResults:\n{result_message}\nTime: {end_time - start_time:.2f}s")
    return result_message

class TombstoneParserCardsInfo(ScrollArea):
    """ TombstoneParserCardsInfo Subinterface """

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

class TombstoneParserInterface:
    def __init__(self, parent=None, mainWindow=None):
        self.parent = parent
        self.mainWindow = mainWindow

    def addTab(self, routeKey, text, icon):
        logger.info('[LIUQI]add tab {} {}'.format(routeKey, text))
        self.mainWindow.tabBar.addTab(routeKey, text, icon)

        # tab左对齐
        self.mainWindow.showInterface.addWidget(TombstoneParserCardsInfo(routeKey=routeKey))
        self.mainWindow.showInterface.setCurrentWidget(self.mainWindow.showInterface.findChild(TombstoneParserCardsInfo, routeKey))
        self.mainWindow.stackedWidget.setCurrentWidget(self.mainWindow.showInterface)
        self.mainWindow.tabBar.setCurrentIndex(self.mainWindow.tabBar.count() - 1)

