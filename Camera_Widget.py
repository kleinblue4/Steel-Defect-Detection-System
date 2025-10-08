from PyQt5.QtWidgets import QPushButton, QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QTimer, Qt
from datetime import datetime
from qfluentwidgets import TransparentToolButton
from qfluentwidgets import FluentIcon as FIF
from Capture import Camera
from Button_Style import Btn_Style
import cv2


class CameraWidget(QWidget):
    def __init__(self, main_stack):
        super().__init__()
        self.main_stack = main_stack
        self.initUI()
        self.camera = Camera()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)

    def initUI(self):
        self.setStyleSheet("background-color: rgb(30, 30, 30);")  # 背景色
        main_layout = QHBoxLayout()  # 主布局横向排列

        # 按钮布局
        btn_layout = QVBoxLayout()  # 纵向排列按钮
        self.open_btn = TransparentToolButton(FIF.VIEW, self)
        self.open_btn.setToolTip("打开摄像头")
        self.capture_btn = TransparentToolButton(FIF.CAMERA, self)
        self.capture_btn.setToolTip("拍摄")
        self.close_btn = TransparentToolButton(FIF.HIDE, self)
        self.close_btn.setToolTip("关闭摄像头")
        self.return_btn = TransparentToolButton(FIF.RETURN, self)
        self.return_btn.setToolTip("返回主界面")

        self.open_btn.clicked.connect(self.open_camera)
        self.capture_btn.clicked.connect(self.capture_image)
        self.close_btn.clicked.connect(self.close_camera)
        self.return_btn.clicked.connect(self.return_to_main_menu)

        # 将按钮添加到左侧
        btn_layout.addWidget(self.open_btn)
        btn_layout.addWidget(self.capture_btn)
        btn_layout.addWidget(self.close_btn)
        btn_layout.addWidget(self.return_btn)
        btn_layout.addStretch()  # 添加弹性空间，使按钮紧凑排列

        # ===== 摄像头预览（右侧）=====
        self.label = QLabel("摄像头预览")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("color: white; font-size: 18px;")

        # 将左右两部分添加到主布局
        main_layout.addLayout(btn_layout)  # 左侧按钮
        main_layout.addWidget(self.label)  # 右侧摄像头预览
        self.setLayout(main_layout)

    def return_to_main_menu(self):
        self.close_camera()  # 关闭摄像头，释放资源
        self.main_stack.setCurrentIndex(0)  # 切换回主菜单

    def open_camera(self):
        try:
            self.camera.open_camera(0)  # 调用 Camera 类打开摄像头
            self.timer.start(30)  # 启动定时器，每 30ms 更新画面
        except AssertionError as e:
            print(str(e))

    def update_frame(self):
        frame = self.camera.show_capture_frame()
        if frame is not None:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            qimg = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.label.setPixmap(QPixmap.fromImage(qimg))

    def capture_image(self):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.camera.save_capture_image(f"capture_{timestamp}")

    def close_camera(self):
        self.timer.stop()
        self.camera.close_camera()
        self.label.setText("摄像头已关闭")

    def closeEvent(self, event):
        self.close_camera()  # 窗口关闭时释放资源
        event.accept()
