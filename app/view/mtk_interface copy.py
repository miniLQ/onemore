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
from pathlib import Path

from PyQt6.QtCore import Qt, QPoint, QSize, QUrl, QRect, QPropertyAnimation
from PyQt6.QtGui import QIcon, QFont, QColor, QPainter
from PyQt6.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QGraphicsOpacityEffect

from qfluentwidgets import (CardWidget, setTheme, Theme, IconWidget, BodyLabel, CaptionLabel, PushButton,
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


class AppCard(CardWidget):
    """ App card """

    def __init__(self, icon, title, content, parent=None):
        super().__init__(parent)
        self.iconWidget = IconWidget(icon)
        self.titleLabel = BodyLabel(title, self)
        self.contentLabel = CaptionLabel(content, self)
        self.openButton = PushButton('打开', self)
        self.moreButton = TransparentToolButton(FluentIcon.MORE, self)

        self.hBoxLayout = QHBoxLayout(self)
        self.vBoxLayout = QVBoxLayout()

        self.setFixedHeight(73)
        self.iconWidget.setFixedSize(48, 48)
        self.contentLabel.setTextColor("#606060", "#d2d2d2")
        self.openButton.setFixedWidth(120)

        self.hBoxLayout.setContentsMargins(20, 11, 11, 11)
        self.hBoxLayout.setSpacing(15)
        self.hBoxLayout.addWidget(self.iconWidget)

        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.addWidget(self.titleLabel, 0, Qt.AlignmentFlag.AlignVCenter)
        self.vBoxLayout.addWidget(self.contentLabel, 0, Qt.AlignmentFlag.AlignVCenter)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.hBoxLayout.addLayout(self.vBoxLayout)

        self.hBoxLayout.addStretch(1)
        self.hBoxLayout.addWidget(self.openButton, 0, Qt.AlignmentFlag.AlignRight)
        self.hBoxLayout.addWidget(self.moreButton, 0, Qt.AlignmentFlag.AlignRight)

        self.moreButton.setFixedSize(32, 32)
        self.moreButton.clicked.connect(self.onMoreButtonClicked)

    def onMoreButtonClicked(self):
        menu = RoundMenu(parent=self)
        menu.addAction(Action(FluentIcon.SHARE, '共享', self))
        menu.addAction(Action(FluentIcon.CHAT, '写评论', self))
        menu.addAction(Action(FluentIcon.PIN, '固定到任务栏', self))

        x = (self.moreButton.width() - menu.width()) // 2 + 10
        pos = self.moreButton.mapToGlobal(QPoint(x, self.moreButton.height()))
        menu.exec(pos)

class AppInfoCard(SimpleCardWidget):
    """ App information card """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.iconLabel = ImageLabel(":/qfluentwidgets/images/logo.png", self)
        self.iconLabel.setBorderRadius(8, 8, 8, 8)
        self.iconLabel.scaledToWidth(120)

        self.nameLabel = TitleLabel('QFluentWidgets', self)
        self.installButton = PrimaryPushButton('打开', self)
        self.companyLabel = HyperlinkLabel(
            QUrl('https://qfluentwidgets.com'), 'Shokokawaii Inc.', self)
        self.installButton.setFixedWidth(160)

        self.descriptionLabel = BodyLabel(
            'PyQt-Fluent-Widgets 是一个基于 PyQt/PySide 的 Fluent Design 风格组件库，包含许多美观实用的组件，支持亮暗主题无缝切换和自定义主题色，帮助开发者快速实现美观优雅的现代化界面。', self)
        self.descriptionLabel.setWordWrap(True)

        self.tagButton = PillPushButton('组件库', self)
        self.tagButton.setCheckable(False)
        setFont(self.tagButton, 12)
        self.tagButton.setFixedSize(80, 32)

        self.shareButton = TransparentToolButton(FluentIcon.SHARE, self)
        self.shareButton.setFixedSize(32, 32)
        self.shareButton.setIconSize(QSize(14, 14))

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
        self.topLayout.addWidget(self.installButton, 0, Qt.AlignmentFlag.AlignRight)

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
        self.buttonLayout.addWidget(self.shareButton, 0, Qt.AlignmentFlag.AlignRight)

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
            'resource/shoko1.jpg', 'resource/shoko2.jpg',
            'resource/shoko3.jpg', 'resource/shoko4.jpg',
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

class MtkInterface(SmoothScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)

        # MTK Tools label
        #self.mtktoolsLabel = QLabel(self.tr("MtkTools"), self)

        self.vBoxLayout = QVBoxLayout(self)

        self.vBoxLayout.setSpacing(6)
        self.vBoxLayout.setContentsMargins(30, 60, 30, 30)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

        suffix = ":/qfluentwidgets/images/controls"
        self.addCard(f":/qfluentwidgets/images/logo.png", "Ramdump Parser", 'designed by iliuqi.')
        self.addCard(f"{suffix}/TitleBar.png", "PyQt-Frameless-Window", 'designed by iliuqi.')
        self.addCard(f"{suffix}/RatingControl.png", "反馈中心", 'designed by iliuqi.')
        self.addCard(f"{suffix}/Checkbox.png", "Microsoft 使用技巧", 'designed by iliuqi.')
        self.addCard(f"{suffix}/Pivot.png", "MSN 天气", 'designed by iliuqi.')
        self.addCard(f"{suffix}/MediaPlayerElement.png", "电影和电视", 'designed by iliuqi.')
        self.addCard(f"{suffix}/PersonPicture.png", "照片", 'designed by iliuqi.')

        self.addCard(f":/qfluentwidgets/images/logo.png", "Ramdump Parser", 'designed by iliuqi.')
        self.addCard(f"{suffix}/TitleBar.png", "PyQt-Frameless-Window", 'designed by iliuqi.')
        self.addCard(f"{suffix}/RatingControl.png", "反馈中心", 'designed by iliuqi.')
        self.addCard(f"{suffix}/Checkbox.png", "Microsoft 使用技巧", 'designed by iliuqi.')
        self.addCard(f"{suffix}/Pivot.png", "MSN 天气", 'designed by iliuqi.')
        self.addCard(f"{suffix}/MediaPlayerElement.png", "电影和电视", 'designed by iliuqi.')
        self.addCard(f"{suffix}/PersonPicture.png", "照片", 'designed by iliuqi.')

        self.addCard(f":/qfluentwidgets/images/logo.png", "Ramdump Parser", 'designed by iliuqi.')
        self.addCard(f"{suffix}/TitleBar.png", "PyQt-Frameless-Window", 'designed by iliuqi.')
        self.addCard(f"{suffix}/RatingControl.png", "反馈中心", 'designed by iliuqi.')
        self.addCard(f"{suffix}/Checkbox.png", "Microsoft 使用技巧", 'designed by iliuqi.')
        self.addCard(f"{suffix}/Pivot.png", "MSN 天气", 'designed by iliuqi.')
        self.addCard(f"{suffix}/MediaPlayerElement.png", "电影和电视", 'designed by iliuqi.')
        self.addCard(f"{suffix}/PersonPicture.png", "照片", 'designed by iliuqi.')

        self.__initWidget()

        # customize scroll animation
        self.setScrollAnimation(Qt.Orientation.Vertical, 500, QEasingCurve.Type.OutQuint)
        self.setScrollAnimation(Qt.Orientation.Horizontal, 500, QEasingCurve.Type.OutQuint)

        self.horizontalScrollBar().setValue(1900)
        #self.setWidget(self.label)
        self.resize(960, 640)



    def addCard(self, icon, title, content):
        card = AppCard(icon, title, content, self)
        self.vBoxLayout.addWidget(card, alignment=Qt.AlignmentFlag.AlignTop)

        
    def __initWidget(self):
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 100, 0, 20)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.setObjectName('MtkInterface')

        # initialize style sheet
        self.scrollWidget.setObjectName('scrollWidget')
        StyleSheet.SETTING_INTERFACE.apply(self)
        self.scrollWidget.setStyleSheet("QWidget{background:transparent}")

        # initialize layout
        # self.__initLayout()
        # self._connectSignalToSlot()