# coding: utf-8
from pathlib import Path

from PyQt6.QtCore import Qt, QSize, QUrl, QPoint
from PyQt6.QtGui import QIcon, QColor
from PyQt6.QtWidgets import QApplication

from qfluentwidgets import NavigationItemPosition, MSFluentWindow, SplashScreen
from qfluentwidgets import FluentIcon as FIF
from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QApplication, QFrame, QStackedWidget
from qfluentwidgets import (NavigationItemPosition, MessageBox, MSFluentTitleBar, MSFluentWindow,
                            TabBar, SubtitleLabel, setFont, TabCloseButtonDisplayMode, IconWidget,
                            TransparentDropDownToolButton, TransparentToolButton, setTheme, Theme,
                            isDarkTheme)

from plugins.plugin_loader import load_plugins

from .setting_interface import SettingInterface
from .mtk_interface import MtkInterface
from .qcom_interface import QcomInterface
from .general_interface import GeneralInterface
from ..common.config import cfg
from ..common.icon import Icon
from ..common.signal_bus import signalBus
from ..common import resource
from ..common.logging import logger

from plugins.plugin_market import PluginMarket

class Widget(QFrame):

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.label = SubtitleLabel(text, self)
        self.hBoxLayout = QHBoxLayout(self)

        setFont(self.label, 24)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hBoxLayout.addWidget(self.label, 1, Qt.AlignmentFlag.AlignCenter)
        self.setObjectName(text.replace(' ', '-'))

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

class CustomTitleBar(MSFluentTitleBar):
    """ Title bar with icon and title """

    def __init__(self, parent):
        super().__init__(parent)

        # add buttons
        #self.toolButtonLayout = QHBoxLayout()
        #color = QColor(206, 206, 206) if isDarkTheme() else QColor(96, 96, 96)
        #self.searchButton = TransparentToolButton(FIF.SEARCH_MIRROR.icon(color=color), self)
        #self.forwardButton = TransparentToolButton(FIF.RIGHT_ARROW.icon(color=color), self)
        #self.backButton = TransparentToolButton(FIF.LEFT_ARROW.icon(color=color), self)

        #self.forwardButton.setDisabled(True)
        #self.toolButtonLayout.setContentsMargins(20, 0, 20, 0)
        #self.toolButtonLayout.setSpacing(15)
        #self.toolButtonLayout.addWidget(self.searchButton)
        #self.toolButtonLayout.addWidget(self.backButton)
        #self.toolButtonLayout.addWidget(self.forwardButton)
        #self.hBoxLayout.insertLayout(4, self.toolButtonLayout)

        # add tab bar
        self.tabBar = TabBar(self)

        # 设置标签是否可移动
        self.tabBar.setMovable(True)
        # 设置标签的最大宽度
        self.tabBar.setTabMaximumWidth(200)
        # 设置标签的阴影
        self.tabBar.setTabShadowEnabled(True)
        # 设置标签选择后的颜色
        self.tabBar.setTabSelectedBackgroundColor(QColor(255, 255, 255, 125), QColor(255, 255, 255, 50))
        # 设置标签是否可以滚动
        self.tabBar.setScrollable(True)
        # 设置标签的关闭按钮显示模式
        self.tabBar.setCloseButtonDisplayMode(TabCloseButtonDisplayMode.ON_HOVER)

        # 设置标签关闭的信号处理
        #self.tabBar.tabCloseRequested.connect(self.removetab)
        # 设置标签切换的信号处理
        self.tabBar.currentChanged.connect(lambda i: self.tabBar.tabText(i))
        
        self.hBoxLayout.insertWidget(4, self.tabBar, 1)
        self.hBoxLayout.setStretch(5, 0)

        # add avatar
        #self.avatar = TransparentDropDownToolButton('resource/shoko.png', self)
        #self.avatar.setIconSize(QSize(26, 26))
        #self.avatar.setFixedHeight(30)
        #self.hBoxLayout.insertWidget(7, self.avatar, 0, Qt.AlignmentFlag.AlignRight)
        #self.hBoxLayout.insertSpacing(8, 20)

    def canDrag(self, pos: QPoint):
        if not super().canDrag(pos):
            return False

        pos.setX(pos.x() - self.tabBar.x())
        return not self.tabBar.tabRegion().contains(pos)

class MainWindow(MSFluentWindow):

    def __init__(self):
        super().__init__()

        self.setTitleBar(CustomTitleBar(self))
        self.tabBar = self.titleBar.tabBar  # type: TabBar
        self.tabBar.tabCloseRequested.connect(self.removetab)
        self.pluginOpenerMap = {}
        self.tabChangedHandlers = {}
        self.TabRouteKeys = []

                
        #self.tabBar.currentChanged.connect(self.onTabChanged)

        # TODO: create sub interface
        self.settingInterface = SettingInterface(self)
        self.generalInterface = GeneralInterface(self)
        self.showInterface = QStackedWidget(self, objectName='showInterface')
        self.homeInterface = QStackedWidget(self, objectName='homeInterface')
        self.qcomInterface = QcomInterface(self)
        self.mtkInterface = MtkInterface(self)

        load_plugins(self)# add interfaces to showInterface

        # 在homeinterface的正中央添加一个widget，显示ONEMORE字符串
        homewidget = Widget('ONEMORE', self.homeInterface)
        self.homeInterface.addWidget(homewidget)
        self.homeInterface.setCurrentWidget(homewidget)

        # 当点击home的tab时，显示homewidget
        #self.addTab('ONEMORE', 'ONEMORE', 'resource/Smiling_with_heart.png')
        #self.homeInterface.show()


        self.connectSignalToSlot()

        # add items to navigation interface
        self.initNavigation()
        self.initWindow()

        self.splashScreen.finish()

    def connectSignalToSlot(self):
        signalBus.micaEnableChanged.connect(self.setMicaEffectEnabled)

    def initNavigation(self):
        # self.navigationInterface.setAcrylicEnabled(True)

        # TODO: add navigation items
        # self.addSubInterface(self.homeInterface, FIF.HOME, self.tr('Home'))

        # create sub interface
        self.addSubInterface(self.homeInterface, FIF.HOME, '主页', FIF.HOME_FILL)
        self.addSubInterface(self.showInterface, FIF.TAG, 'TAB', FIF.TAG, NavigationItemPosition.BOTTOM)
        self.addSubInterface(self.generalInterface, FIF.APPLICATION, '通用')
        self.addSubInterface(self.mtkInterface, FIF.APPLICATION, 'MTK')
        self.addSubInterface(self.qcomInterface, FIF.APPLICATION, '高通')

        self.pluginMarketInterface = PluginMarket("plugins", self)
        self.pluginMarketInterface.setObjectName("plugin-market")

        self.addSubInterface(
            self.pluginMarketInterface,
            FIF.SHOPPING_CART,
            '插件市场',
            FIF.SHOPPING_CART,
            NavigationItemPosition.BOTTOM
        )

        # add custom widget to bottom
        self.addSubInterface(
            self.settingInterface, Icon.SETTINGS, self.tr('Settings'), Icon.SETTINGS_FILLED, NavigationItemPosition.BOTTOM)
        
        # add tab
        #self.addTab('Heart', 'As long as you love me', icon='resource/Heart.png')

        self.tabBar.currentChanged.connect(self.onTabChanged)

        # 遍歷pluginOpenerMap, 將這個UNIQUE_NAME添加到tabBar中的currentChanged.connect，也就是self.onTabChanged
        # for uniqueName, openFunc in self.pluginOpenerMap.items():
        #     # create a tab for each plugin
        #     ramdomNum = cfg.get(cfg.randomNum)
        #     routeKey = f"{uniqueName} {ramdomNum}"
        #     self.addTab(routeKey, uniqueName, 'app/resource/images/Chicken.png')
        #
        #     # connect the tab to the open function
        #     self.tabBar.currentChanged.connect(lambda index, func=openFunc: func())


        # 设置默认显示HOME界面
        self.homeInterface.show()

        #self.tabBar.tabAddRequested.connect(self.onTabAddRequested)

    def initWindow(self):
        self.resize(1100, 750)
        #self.setMinimumWidth(760)
        self.setWindowIcon(QIcon(':/app/images/logo.png'))
        self.setWindowTitle('OneMore')

        self.setCustomBackgroundColor(QColor(240, 244, 249), QColor(32, 32, 32))
        self.setMicaEffectEnabled(cfg.get(cfg.micaEnabled))

        # create splash screen
        self.splashScreen = SplashScreen(self.windowIcon(), self)
        self.splashScreen.setIconSize(QSize(106, 106))
        self.splashScreen.raise_()

        desktop = QApplication.primaryScreen().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)
        self.show()
        QApplication.processEvents()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if hasattr(self, 'splashScreen'):
            self.splashScreen.resize(self.size())
    
    def onTabChanged(self, index: int):
        objectName = self.tabBar.currentTab().routeKey()
        # 插件注册的处理逻辑
        for keyword, handler in self.tabChangedHandlers.items():
            if keyword in objectName:
                handler(objectName)
                return

        # if "Linux Ramdump" in objectName:
        #     logger.info('[TAB CHANGED] Tab change to {}'.format(objectName))
        #     self.showInterface.setCurrentWidget(self.showInterface.findChild(LinuxRamdumpParserCardsInfo, objectName))
        # if "Aee Extractor" in objectName:
        #     logger.info('[TAB CHANGED] Tab change to {}'.format(objectName))
        #     self.showInterface.setCurrentWidget(self.showInterface.findChild(AeeExtractorCardsInfo, objectName))
        # elif "Android Image Unpack" in objectName:
        #     logger.info('[TAB CHANGED] Tab change to {}'.format(objectName))
        #     self.showInterface.setCurrentWidget(self.showInterface.findChild(AndroidImagesEditorCardsInfo, objectName))
        # elif "NE/KE-Analyze" in objectName:
        #     logger.info('[TAB CHANGED] Tab change to {}'.format(objectName))
        #     self.showInterface.setCurrentWidget(self.showInterface.findChild(NeKeAnalyzeCardsInfo, objectName))
        # elif "StartGDB" in objectName:
        #     logger.info('[TAB CHANGED] Tab change to {}'.format(objectName))
        #     self.showInterface.setCurrentWidget(self.showInterface.findChild(StartGDBCardsInfo, objectName))
        # elif "NOC Decode" in objectName:
        #     logger.info('[TAB CHANGED] Tab change to {}'.format(objectName))
        #     self.showInterface.setCurrentWidget(self.showInterface.findChild(NocDecodeCardsInfo, objectName))
        # elif "Memory Analyzer tool" in objectName:
        #     logger.info('[TAB CHANGED] Tab change to {}'.format(objectName))
        #     self.showInterface.setCurrentWidget(self.showInterface.findChild(MatCardsInfo, objectName))
        # elif "Tombstone_Praser" in objectName:
        #     logger.info('[TAB CHANGED] Tab change to {}'.format(objectName))
        #     self.showInterface.setCurrentWidget(self.showInterface.findChild(TombstoneParserCardsInfo, objectName))
        # elif "TzLog_Parser" in objectName:
        #     logger.info('[TAB CHANGED] Tab change to {}'.format(objectName))
        #     self.showInterface.setCurrentWidget(self.showInterface.findChild(TzErrorCodeDecodeCardsInfo, objectName))
        # else:
        #     self.showInterface.setCurrentWidget(self.showInterface.findChild(TabInterface, objectName))

        self.stackedWidget.setCurrentWidget(self.showInterface)
        self.tabBar.setCurrentIndex(index)

    def onTabAddRequested(self):
        text = f'硝子酱一级棒卡哇伊×{self.tabBar.count()}'
        self.addTab(text, text, 'resource/Smiling_with_heart.png')

    def addTab(self, routeKey, text, icon):
        logger.info('[TAB ADD] {}'.format(routeKey))
        self.tabBar.addTab(routeKey, text, icon)

        # tab左对齐
        self.showInterface.addWidget(TabInterface(text, icon, routeKey, self))

    def removetab(self, index: int):
        # 獲取指定index的tab的routeKey
        routekey = self.tabBar.items[index]._routeKey

        logger.info('[TAB REMOVE] {}'.format(routekey))
        self.tabBar.removeTab(index)
        self.showInterface.removeWidget(self.showInterface.widget(index))
        self.showInterface.setCurrentIndex(0)

        # 在移除tab時，刪除self.TabRouteKeys中的對應routeKey
        if routekey in self.TabRouteKeys:
            self.TabRouteKeys.remove(routekey)

    def registerPluginOpener(self, uniqueName: str, openFunc: callable):
        self.pluginOpenerMap[uniqueName] = openFunc

    def registerTabChangedHandler(self, keyword: str, handler: callable):
        self.tabChangedHandlers[keyword] = handler