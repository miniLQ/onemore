# coding:utf-8
from qfluentwidgets import (SwitchSettingCard, FolderListSettingCard,
                            OptionsSettingCard, PushSettingCard,
                            HyperlinkCard, PrimaryPushSettingCard, ScrollArea,
                            ComboBoxSettingCard, ExpandLayout, Theme, CustomColorSettingCard,
                            setTheme, setThemeColor, isDarkTheme, setFont)
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import SettingCardGroup as CardGroup
from qfluentwidgets import InfoBar
from PyQt6.QtCore import Qt, pyqtSignal, QUrl, QStandardPaths, QEasingCurve
from PyQt6.QtGui import QDesktopServices, QFont
from PyQt6.QtWidgets import QWidget, QLabel, QFileDialog

import sys
import random
from pathlib import Path

from PyQt6.QtCore import Qt, QPoint, QSize, QUrl, QRect, QPropertyAnimation
from PyQt6.QtGui import QIcon, QFont, QColor, QPainter
from PyQt6.QtWidgets import QApplication, QWidget, QFrame,QHBoxLayout, QVBoxLayout, QGraphicsOpacityEffect

from qfluentwidgets import (CardWidget, SubtitleLabel, setTheme, Theme, IconWidget, BodyLabel, CaptionLabel, PushButton,
                            TransparentToolButton, FluentIcon, RoundMenu, Action, ElevatedCardWidget,
                            ImageLabel, isDarkTheme, FlowLayout, MSFluentTitleBar, SimpleCardWidget,
                            HeaderCardWidget, InfoBarIcon, HyperlinkLabel, HorizontalFlipView,
                            PrimaryPushButton, TitleLabel, PillPushButton, setFont, ScrollArea,
                            VerticalSeparator, MSFluentWindow, NavigationItemPosition, GroupHeaderCardWidget,
                            ComboBox, SearchLineEdit, SmoothScrollArea)

from qfluentwidgets.components.widgets.acrylic_label import AcrylicBrush

def isWin11():
    return sys.platform == 'win32' and sys.getwindowsversion().build >= 22000

if isWin11():
    from qframelesswindow import AcrylicWindow as Window
else:
    from qframelesswindow import FramelessWindow as Window


from ..common.config import cfg, isWin11
from ..common.setting import HELP_URL, FEEDBACK_URL, AUTHOR, VERSION, YEAR
from ..common.signal_bus import signalBus
from ..common.style_sheet import StyleSheet
from ..common.logging import logger
from ..common.utils import generate_uuid

from .mtk_subinterface.AeeExtractorinterface import AeeExtractorInterface

TOOL1_UNIQUE_NAME = "AeeDBExtractor"
TOOL2_UNIQUE_NAME = "TOOL2"
TOOL3_UNIQUE_NAME = "TOOL3"
TOOL4_UNIQUE_NAME = "TOOL4"
TOOL5_UNIQUE_NAME = "TOOL5"
TOOL6_UNIQUE_NAME = "TOOL6"
TOOL7_UNIQUE_NAME = "TOOL7"

class TabInterface(QFrame):
    """ Tab interface """

    def __init__(self, text: str, icon, objectName, parent=None):
        super().__init__(parent=parent)
        # use big image
        icon = Path(icon)
        icon = icon.parent / f"{icon.stem}_big{icon.suffix}"

        self.iconWidget = IconWidget(str(icon), self)
        self.label = SubtitleLabel(text, self)
        self.iconWidget.setFixedSize(120, 120)

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.vBoxLayout.setSpacing(30)
        self.vBoxLayout.addWidget(self.iconWidget, 0, Qt.AlignmentFlag.AlignCenter)
        self.vBoxLayout.addWidget(self.label, 0, Qt.AlignmentFlag.AlignCenter)
        setFont(self.label, 24)

        self.setObjectName(objectName)

class AppCard(CardWidget):
    """ App card """

    def __init__(self, icon, title, content, parent=None, UniqueName=None, mainWindow=None):
        super().__init__(parent=parent)
        self.mainWindow = mainWindow
        self.UniqueName = UniqueName
        self.iconWidget = IconWidget(icon)
        self.titleLabel = BodyLabel(title, self)
        self.contentLabel = CaptionLabel(content, self)
        self.openButton = PushButton('打开', self)
        self.openButton.clicked.connect(self.onOpenButtonClicked)
        #self.moreButton = TransparentToolButton(FluentIcon.MORE, self)

        self.hLayout = QHBoxLayout(self)
        self.vLayout = QVBoxLayout()

        self.setFixedHeight(70)
        self.iconWidget.setFixedSize(48, 48)
        self.contentLabel.setTextColor("#606060", "#d2d2d2")
        self.openButton.setFixedWidth(120)

        self.hLayout.setContentsMargins(20, 11, 11, 11)
        self.hLayout.setSpacing(15)
        self.hLayout.addWidget(self.iconWidget)

        self.vLayout.setContentsMargins(0, 0, 0, 0)
        self.vLayout.setSpacing(0)
        self.vLayout.addWidget(self.titleLabel, 0, Qt.AlignmentFlag.AlignVCenter)
        self.vLayout.addWidget(self.contentLabel, 0, Qt.AlignmentFlag.AlignVCenter)
        self.vLayout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.hLayout.addLayout(self.vLayout)

        self.hLayout.addStretch(1)
        self.hLayout.addWidget(self.openButton, 0, Qt.AlignmentFlag.AlignRight)
        #self.hBoxLayout.addWidget(self.moreButton, 0, Qt.AlignmentFlag.AlignRight)

        #self.moreButton.setFixedSize(32, 32)
        #self.moreButton.clicked.connect(self.onMoreButtonClicked)

    def onMoreButtonClicked(self):
        menu = RoundMenu(parent=self)
        menu.addAction(Action(FluentIcon.SHARE, '共享', self))
        menu.addAction(Action(FluentIcon.CHAT, '写评论', self))
        menu.addAction(Action(FluentIcon.PIN, '固定到任务栏', self))

        x = (self.moreButton.width() - menu.width()) // 2 + 10
        pos = self.moreButton.mapToGlobal(QPoint(x, self.moreButton.height()))
        menu.exec(pos)

    def onOpenButtonClicked(self):
        #print('open button clicked')
        logger.info("{} button clicked!".format(self.UniqueName))
        # 根据self.UniqueName()来判断点击的是哪个按钮,然后执行相应函数
        if self.UniqueName == TOOL1_UNIQUE_NAME:
            # 打开AeeExtractor
            # 创建一个标签页
            # 生成一个7位的guid随机数
            ramdomNum = generate_uuid()
            routekey = "Aee Extractor {}".format(ramdomNum)
            self.AeeExtractorInterface = AeeExtractorInterface(mainWindow=self.mainWindow)
            self.AeeExtractorInterface.addTab(routeKey=routekey, text=routekey, icon='resource/images/Smiling_with_heart.png')

            # 切换到homeinterface
            #self.mainWindow.switchTo(self.mainWindow.homeInterface)
            # 切换到新建的tab
            #print("routekey:{}".format(routekey))
            #self.mainWindow.tabBar.setCurrentTab(routeKey=routekey)
            #aeeextractorsubinterface = AeeExtractorSubinterface()
            pass
        elif self.UniqueName == TOOL2_UNIQUE_NAME:
            # 打开Tool2
            # ramdomNum = random.randint(1000000, 9999999)
            # self.mainWindow.addTab("Test Tool 2 {}".format(ramdomNum), "Test Tool 2 {}".format(ramdomNum), 'resource/Smiling_with_heart.png')
            
            # # 切换到homeinterface
            # self.mainWindow.switchTo(self.mainWindow.homeInterface)
            # # 切换到新建的tab
            # self.mainWindow.tabBar.setCurrentTab(routeKey="Test Tool 2 {}".format(ramdomNum))
            # #aeeextractorsubinterface = AeeExtractorSubinterface()
            pass
        elif self.UniqueName == TOOL3_UNIQUE_NAME:
            # 打开Tool3
            pass
        elif self.UniqueName == TOOL4_UNIQUE_NAME:
            # 打开Tool4
            pass
        elif self.UniqueName == TOOL5_UNIQUE_NAME:
            # 打开Tool5
            pass
        elif self.UniqueName == TOOL6_UNIQUE_NAME:
            # 打开Tool6
            pass
        elif self.UniqueName == TOOL7_UNIQUE_NAME:
            # 打开Tool7
            pass
        else:
            logger.error("Unknown tool")
    

class MtkInterface(ScrollArea):
    """ Mtk tools interface """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.parent = parent
        self.scrollAreaWidgetContents = QWidget()
        # 垂直布局
        self.expandLayout = ExpandLayout(self.scrollAreaWidgetContents)
        #self.flowlayout = FlowLayout(self.scrollAreaWidgetContents)

        #self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        #self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setObjectName('mtkInterface')
        self.setWidgetResizable(True)

        # setting label
        # 瀑布式布局
        # self.mtktoolsLabel = QLabel(self.tr("MTK TOOLS"), self)
        # self.vBoxLayout = QVBoxLayout(self.scrollAreaWidgetContents)
        # self.vBoxLayout.setSpacing(6)
        # self.vBoxLayout.setContentsMargins(50, 100, 50, 100)
        # self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

        #self.parent.tabBar.currentChanged.connect(self.parent.onTabChanged)
        #self.parent.tabBar.tabAddRequested.connect(self.parent.onTabAddRequested)

        self.__initWidget()

        suffix = ":/qfluentwidgets/images/controls"
        self.addCard(f":/qfluentwidgets/images/logo.png", "AEE DB Extract", '@designed by iliuqi.', TOOL1_UNIQUE_NAME)
        #self.addCard(f"{suffix}/TitleBar.png", "Test Tool 2", '@designed by iliuqi.', TOOL2_UNIQUE_NAME)
        #self.addCard(f"{suffix}/RatingControl.png", "Test Tool 3", '@designed by iliuqi.', TOOL3_UNIQUE_NAME)
        #self.addCard(f"{suffix}/Checkbox.png", "Test Tool 4", '@designed by iliuqi.', TOOL4_UNIQUE_NAME)
        #self.addCard(f"{suffix}/Pivot.png", "Test Tool 5", '@designed by iliuqi.', TOOL5_UNIQUE_NAME)
        #self.addCard(f"{suffix}/MediaPlayerElement.png", "Test Tool 6", '@designed by iliuqi.', TOOL6_UNIQUE_NAME)
        #self.addCard(f"{suffix}/PersonPicture.png", "Test Tool 7", '@designed by iliuqi.', TOOL7_UNIQUE_NAME)


    def addCard(self, icon, title, content, UniqueName):
        card = AppCard(icon=icon, title=title, content=content, parent=self.scrollAreaWidgetContents, UniqueName=UniqueName, mainWindow=self.parent)
        
        # 将card组件加入到设置好的滚动布局中
        self.expandLayout.addWidget(card)

        #self.flowlayout.addWidget(card)

        #self.vBoxLayout.addWidget(card, alignment=Qt.AlignmentFlag.AlignTop)


    def __initWidget(self):
        self.setWidget(self.scrollAreaWidgetContents)
        self.scrollAreaWidgetContents.setMinimumSize(500, 500)
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")