from PyQt5.QtCore import Qt, QRectF, QUrl, QLocale
from PyQt5.QtGui import QPixmap, QPainter, QColor, QBrush, QPainterPath, QLinearGradient, QDesktopServices, QFont
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QApplication, QHBoxLayout, QFrame, QPushButton, QGridLayout, \
    QSizePolicy, QSpacerItem, QStackedWidget, QMainWindow
import sys
from qfluentwidgets import ScrollArea, isDarkTheme, FluentIcon, SingleDirectionScrollArea, IconWidget, TextWrap, \
    qconfig, setTheme, Theme, TitleLabel, SubtitleLabel
# from QCandyUi import CandyWindow
from Kimi_Chat_Widget import KimiChatWidget
from Data_Annotator import DataAnnotator
from Camera_Widget import CameraWidget
from Data_Base_Widget import DataBaseWidget
from Reasoning_Widget import ReasoningWidget
from qfluentwidgets import (qconfig, QConfig, ConfigItem, OptionsConfigItem, BoolValidator,
                            OptionsValidator, RangeConfigItem, RangeValidator,
                            FolderListValidator, Theme, FolderValidator, ConfigSerializer, __version__)
import os
os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = "/opt/conda/envs/defect_env/lib/python3.10/site-packages/PyQt5/Qt5/plugins/platforms/"


# class Language(Enum):
#     """ Language enumeration """
#
#     CHINESE_SIMPLIFIED = QLocale(QLocale.Chinese, QLocale.China)
#     CHINESE_TRADITIONAL = QLocale(QLocale.Chinese, QLocale.HongKong)
#     ENGLISH = QLocale(QLocale.English)
#     AUTO = QLocale()
#
#
# class Config(QConfig):
#     """ Config of application """
#
#     # folders
#     musicFolders = ConfigItem(
#         "Folders", "LocalMusic", [], FolderListValidator())
#     downloadFolder = ConfigItem(
#         "Folders", "Download", "app/download", FolderValidator())
#
#     # main window
#     micaEnabled = ConfigItem("MainWindow", "MicaEnabled", isWin11(), BoolValidator())
#     dpiScale = OptionsConfigItem(
#         "MainWindow", "DpiScale", "Auto", OptionsValidator([1, 1.25, 1.5, 1.75, 2, "Auto"]), restart=True)
#     language = OptionsConfigItem(
#         "MainWindow", "Language", Language.AUTO, OptionsValidator(Language), LanguageSerializer(), restart=True)
#
#     # Material
#     blurRadius = RangeConfigItem("Material", "AcrylicBlurRadius", 15, RangeValidator(0, 40))
#
#     # software update
#     checkUpdateAtStartUp = ConfigItem("Update", "CheckUpdateAtStartUp", True, BoolValidator())


class Card(QPushButton):

    def __init__(self, icon, title, content, parent=None):
        super().__init__(parent=parent)

        # 样式设置
        self.setStyleSheet("""
            Card {
                background-color: rgba(255, 255, 255, 150);
                border: none;
                text-align: left;
            }
            Card:hover {
                background-color: rgba(245, 245, 245, 150);
            }
            Card:pressed {
                background-color: rgba(240, 240, 240, 150);
            }
            #titleLabel {
                font: bold 14px 'Segoe UI'; 
                background: transparent;
                color: black;
            }
            #contentLabel {
                font: bold 12px 'Segoe UI';
                background: transparent;
                color: gray;
            }
        """)
        self.setFixedSize(198, 220)

        # 子部件
        self.iconWidget = IconWidget(icon, self)
        self.titleLabel = QLabel(title, self)
        self.contentLabel = QLabel(TextWrap.wrap(content, 28, False)[0], self)

        self.__initWidget()

    def __initWidget(self):
        self.iconWidget.setFixedSize(54, 54)

        # 布局
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(24, 24, 0, 13)
        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.addWidget(self.iconWidget)
        self.vBoxLayout.addSpacing(16)
        self.vBoxLayout.addWidget(self.titleLabel)
        self.vBoxLayout.addSpacing(8)
        self.vBoxLayout.addWidget(self.contentLabel)
        self.vBoxLayout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        # 对象名用于样式表
        self.titleLabel.setObjectName('titleLabel')
        self.contentLabel.setObjectName('contentLabel')

    def resizeCard(self, scale_factor):
        card_width = int(198 * scale_factor)
        card_height = int(220 * scale_factor)
        self.setFixedSize(card_width, card_height)

        # 图标
        self.iconWidget.setFixedSize(int(54 * scale_factor), int(54 * scale_factor))

        # 字体缩放
        title_font = self.titleLabel.font()
        title_font.setPointSizeF(14 * scale_factor)
        self.titleLabel.setFont(title_font)

        content_font = self.contentLabel.font()
        content_font.setPointSizeF(12 * scale_factor)
        self.contentLabel.setFont(content_font)

        # 调整间距
        self.vBoxLayout.setContentsMargins(int(24 * scale_factor), int(24 * scale_factor), 0, int(13 * scale_factor))
        self.vBoxLayout.setSpacing(int(8 * scale_factor))


class CardView(SingleDirectionScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent, Qt.Vertical)
        self.base_width = 700
        self.base_card_width = 198
        self.base_card_height = 220
        self.setStyleSheet("background-color: transparent; border: none;")
        self.view = QWidget(self)

        self.gridLayout = QGridLayout(self.view)
        self.gridLayout.setContentsMargins(20, 20, 36, 20)
        self.gridLayout.setHorizontalSpacing(12)
        self.gridLayout.setVerticalSpacing(12)

        self.titleLabel = TitleLabel('瑕疵检测系统', self.view)
        # self.titleLabel.setStyleSheet("font: bold 18px 'Segoe UI'; color: #333;")
        self.subtitleLabel = SubtitleLabel('\n\n云舟丹心', self.view)
        self.subtitleLabel.setStyleSheet("font: bold 14px 'Segoe UI'; color: grey;")
        self.subtitleLabel.setContentsMargins(0, 20, 20, 0)
        # self.titlelayout = QHBoxLayout(self.view)
        # self.titlelayout.setContentsMargins(0, 0, 0, 0)
        # self.titlelayout.addWidget(self.titleLabel)
        # self.titlelayout.addWidget(self.subtitleLabel)
        self.gridLayout.addWidget(self.titleLabel, 0, 0, alignment=Qt.AlignCenter)
        self.gridLayout.addWidget(self.subtitleLabel, 0, 0, alignment=Qt.AlignRight)

        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.gridLayout.addItem(spacer, 0, 1, 1, 2)

        self.currentRow = 0
        self.currentCol = 1

        self.setWidget(self.view)
        self.setWidgetResizable(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

    def addCard(self, icon, title, content):
        card = Card(icon, title, content, self.view)

        # 动态计算位置
        if self.currentRow == 0:
            if self.currentCol >= 3:
                self.currentRow += 1
                self.currentCol = 0
        else:
            if self.currentCol >= 3:  # 后续行每行3卡片
                self.currentRow += 1
                self.currentCol = 0

        alignment = Qt.AlignRight
        self.gridLayout.addWidget(card, self.currentRow, self.currentCol, alignment=alignment)
        self.currentCol += 1
        return card

    def resizeEvent(self, event):
        super().resizeEvent(event)
        new_width = self.width()
        scale_factor = new_width / self.base_width

        # 调整标题字体
        font = self.titleLabel.font()
        font.setPointSizeF(18 * scale_factor)
        self.titleLabel.setFont(font)

        # 遍历 Card 并缩放尺寸
        for i in range(self.gridLayout.count()):
            item = self.gridLayout.itemAt(i)
            widget = item.widget()
            if isinstance(widget, Card):
                widget.resizeCard(scale_factor)


class mainWin(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle("瑕疵检测系统")
        self.setMinimumSize(500, 400)
        self.setGeometry(100, 100, 700, 550)
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        # self.setMicaEffectEnabled(cfg.get(cfg.micaEnabled))

        setTheme(Theme.LIGHT)

        self.vBoxLayout = QVBoxLayout(self)
        self.banner = QPixmap('./qt_image/header1.png')
        self.CardView = CardView(self)

        self.main_widget = QWidget()

        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.setContentsMargins(0, 20, 0, 0)

        self.kimi_widget = KimiChatWidget(self.stack)
        self.data_annotator_widget = DataAnnotator(self.stack)
        self.camera_widget = CameraWidget(self.stack)
        self.db_widget = DataBaseWidget(self.stack)
        self.reasoning_model_widget = ReasoningWidget(self.stack)

        cards = [
            (FluentIcon.CHAT, 'Kimi AI', 'AI对话与报告生成', 1),
            (FluentIcon.EDIT, '数据标注', '数据标注与处理', 2),
            (FluentIcon.CAMERA, '拍摄', '图像采集与存储', 3),
            (FluentIcon.SYNC, '数据库', '数据管理（查询、插入、\n删除等）', 4),
            (FluentIcon.CERTIFICATE, '模型操作', '模型的训练、评估、推理及\n结果分析', 5)
        ]

        for icon, title, content, index in cards:
            card = self.CardView.addCard(icon, self.tr(title), self.tr(content))
            card.clicked.connect(lambda _, idx=index: self.stack.setCurrentIndex(idx))

        self.vBoxLayout.addWidget(self.CardView, 1)
        self.main_widget.setLayout(self.vBoxLayout)

        # 初始化堆叠窗口内容
        self.stack.addWidget(self.main_widget)  # 索引0: 主界面
        self.stack.addWidget(self.kimi_widget)  # 索引1
        self.stack.addWidget(self.data_annotator_widget)  # 索引2
        self.stack.addWidget(self.camera_widget)  # 索引3
        self.stack.addWidget(self.db_widget)  # 索引4
        self.stack.addWidget(self.reasoning_model_widget)  # 索引5

        # 设置主界面为第一个页面
        self.stack.setCurrentIndex(0)

    def paintEvent(self, e):
        super().paintEvent(e)
        if self.stack.currentIndex() != 0:
            return  # 只在主界面绘制背景图像

        painter = QPainter(self)
        painter.setRenderHints(
            QPainter.SmoothPixmapTransform | QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)

        path = QPainterPath()
        path.setFillRule(Qt.WindingFill)
        w, h = self.width(), self.height()
        path.addRoundedRect(QRectF(0, 0, w, h), 10, 10)
        path.addRect(QRectF(0, h - 50, 50, 50))
        path.addRect(QRectF(w - 50, 0, 50, 50))
        path.addRect(QRectF(w - 50, h - 50, 50, 50))
        path = path.simplified()

        gradient = QLinearGradient(0, 0, 0, h)

        if not isDarkTheme():
            gradient.setColorAt(0, QColor(207, 216, 228, 255))
            gradient.setColorAt(1, QColor(207, 216, 228, 0))
        else:
            gradient.setColorAt(0, QColor(0, 0, 0, 255))
            gradient.setColorAt(1, QColor(0, 0, 0, 0))

        painter.fillPath(path, QBrush(gradient))

        # 绘制 banner 图像
        pixmap = self.banner.scaled(
            self.size(), transformMode=Qt.SmoothTransformation)
        painter.fillPath(path, QBrush(pixmap))


if __name__ == '__main__':
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    app = QApplication(sys.argv)
    w = mainWin()
    w.show()
    app.exec()
