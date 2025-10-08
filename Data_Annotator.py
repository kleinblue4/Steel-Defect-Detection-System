import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFileDialog, QMessageBox, \
    QStackedWidget, QStackedLayout, QScrollArea
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from datetime import datetime
from qfluentwidgets import SubtitleLabel, TransparentToolButton, TextBrowser, PushButton
from Dataset_Build.Data_Make import Data_Generate
from Button_Style import Btn_Style
from Camera_Widget import CameraWidget
from Capture import Camera
from DataBase_Modules.DataBase import DataBase
from qfluentwidgets import FluentIcon as FIF
import cv2


class PhotoTaking(QWidget):
    photoConfirmed = pyqtSignal(str)
    photoCancelled = pyqtSignal()

    def __init__(self, main_stack):
        super().__init__()
        self.label = None
        self.return_btn = None
        self.capture_btn = None
        self.open_btn = None
        self.image_path = None
        self.main_stack = main_stack
        self.camera = Camera()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.initUI()

    def initUI(self):
        self.main_layout = QHBoxLayout()

        # 按钮布局
        btn_layout = QVBoxLayout()
        self.open_btn = TransparentToolButton(FIF.VIEW, self)
        self.open_btn.setToolTip("打开摄像头")
        self.capture_btn = TransparentToolButton(FIF.CAMERA, self)
        self.capture_btn.setToolTip("拍摄")
        self.return_btn = TransparentToolButton(FIF.RETURN, self)
        self.return_btn.setToolTip("返回")

        self.open_btn.clicked.connect(self.open_camera)
        self.capture_btn.clicked.connect(self.capture_image)
        self.return_btn.clicked.connect(self.return_to_main_menu)

        btn_layout.addWidget(self.open_btn)
        btn_layout.addWidget(self.capture_btn)
        btn_layout.addWidget(self.return_btn)
        btn_layout.addStretch()

        self.label = QLabel("摄像头预览")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("color: white; font-size: 18px;background-color: rgb(30, 30, 30);")

        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setFixedSize(640, 480)

        # 选择按钮
        self.confirm_btn = PushButton("确认")
        self.cancel_btn = PushButton("重新拍摄")

        self.confirm_btn.clicked.connect(self.confirm_image)
        self.cancel_btn.clicked.connect(self.retry_capture)

        # 预览按钮布局
        self.preview_layout = QVBoxLayout()
        self.preview_layout.addWidget(self.preview_label)
        self.preview_layout.addWidget(self.confirm_btn)
        self.preview_layout.addWidget(self.cancel_btn)
        self.preview_layout.addStretch()
        self.preview_widget = QWidget()
        self.preview_widget.setLayout(self.preview_layout)
        self.preview_widget.hide()

        # 主布局
        self.main_widget = QWidget()

        self.main_layout.addLayout(btn_layout)
        self.main_layout.addWidget(self.label)
        self.main_widget.setLayout(self.main_layout)

        # 叠加布局
        self.stack_layout = QStackedLayout()
        self.stack_layout.addWidget(self.main_widget)
        self.stack_layout.addWidget(self.preview_widget)

        self.setLayout(self.stack_layout)

    def confirm_image(self):
        """确认照片，返回路径"""
        self.close_camera()
        self.photoConfirmed.emit(self.image_path)
        self.main_stack.setCurrentIndex(0)

    def return_to_main_menu(self):
        """返回时发射取消信号"""
        self.close_camera()
        self.photoCancelled.emit()
        self.main_stack.setCurrentIndex(0)

    def capture_image(self):
        """拍摄照片并显示预览"""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.image_path = f"capture_{timestamp}"
        self.image_path = self.camera.save_capture_image(self.image_path)
        # 显示拍摄的图片
        print(self.image_path)
        pixmap = QPixmap(self.image_path)
        self.preview_label.setPixmap(pixmap.scaled(640, 480, Qt.KeepAspectRatio))
        # 切换到预览界面
        self.stack_layout.setCurrentWidget(self.preview_widget)

    def close_camera(self):
        self.timer.stop()
        self.camera.close_camera()
        self.label.setText("摄像头已关闭")

    def retry_capture(self):
        """重新拍摄，回到主布局"""
        self.stack_layout.setCurrentWidget(self.main_widget)

    def update_frame(self):
        frame = self.camera.show_capture_frame()
        if frame is not None:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            qimg = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.label.setPixmap(QPixmap.fromImage(qimg))

    def closeEvent(self, event):
        self.close_camera()  # 窗口关闭时释放资源
        event.accept()

    def open_camera(self):
        try:
            self.camera.open_camera(0)
            self.timer.start(30)
        except AssertionError as e:
            print(str(e))


class DataAnnotator(QWidget):
    def __init__(self, main_stack):
        super().__init__()
        # self.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.pixmap = None
        self.photo_taking = None
        self.drawing = None
        self.data_generator = None
        self.image_path = None
        self.main_stack = main_stack
        self.stack = QStackedWidget()
        self.db = DataBase("localhost", "root", "123456", "new_table",
                mysql_path='/usr/bin/mysql',
                mysqldump_path='/usr/bin/mysqldump')
        self.initUI()

    def initUI(self):
        main_widget = QWidget()
        main_widget.setAttribute(Qt.WA_TranslucentBackground)
        layout = QHBoxLayout(main_widget)

        image_txt_layout = QVBoxLayout()

        self.image_label = SubtitleLabel("数据标注")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("background-color: rgba(255, 255, 255, 150)")

        # 使用 QScrollArea 来包裹 image_label
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.image_label)

        self.upload_btn = TransparentToolButton(FIF.PHOTO, self)
        self.upload_btn.setToolTip("上传图片")
        self.capture_btn = TransparentToolButton(FIF.CAMERA, self)
        self.capture_btn.setToolTip("拍摄图片")
        self.save_btn = TransparentToolButton(FIF.SAVE, self)
        self.save_btn.setToolTip("保存标注")
        self.switch_defect_btn = TransparentToolButton(FIF.LABEL, self)
        self.switch_defect_btn.setToolTip("切换缺陷类型")
        self.undo_rectangle_btn = TransparentToolButton(FIF.CANCEL, self)
        self.undo_rectangle_btn.setToolTip("撤销上一个标注")
        self.return_btn = TransparentToolButton(FIF.RETURN, self)
        self.return_btn.setToolTip("返回主界面")

        btn_layout = QVBoxLayout()
        btn_layout.addWidget(self.upload_btn)
        btn_layout.addWidget(self.capture_btn)
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.switch_defect_btn)
        btn_layout.addWidget(self.undo_rectangle_btn)
        btn_layout.addWidget(self.return_btn)
        btn_layout.addStretch()

        self.label_display = TextBrowser()
        self.label_display.setReadOnly(True)

        image_txt_layout.addWidget(self.label_display, 1)
        image_txt_layout.addWidget(self.scroll_area, 8)

        layout.addLayout(btn_layout)
        layout.addLayout(image_txt_layout)
        main_widget.setLayout(layout)

        # 将主界面添加到内部堆栈
        self.stack.addWidget(main_widget)

        # 设置 DataAnnotator 的主布局
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.stack)
        self.setLayout(main_layout)

        self.upload_btn.clicked.connect(self.upload_image)
        self.capture_btn.clicked.connect(self.capture_image)
        self.save_btn.clicked.connect(self.save_annotations)
        self.switch_defect_btn.clicked.connect(self.switch_defect)
        self.undo_rectangle_btn.clicked.connect(self.undo_rectangle)
        self.return_btn.clicked.connect(self.return_to_main_menu)

    def upload_image(self):
        file_dialog = QFileDialog()
        self.image_path, _ = file_dialog.getOpenFileName(self, "选择图片", "", "Image Files (*.png *.jpg *.jpeg)")

        if self.image_path:
            self.image_path = os.path.normpath(self.image_path)
            self.image_path = os.path.relpath(self.image_path, start=os.getcwd())
            self.start_annotation(self.image_path)

    def capture_image(self):
        """拍摄图片"""
        if not hasattr(self, 'photo_taking') or self.photo_taking is None:
            self.photo_taking = PhotoTaking(self.stack)

            # 连接信号
            self.photo_taking.photoConfirmed.connect(self.handle_photo_result)
            self.photo_taking.photoCancelled.connect(self.handle_photo_cancel)

            self.stack.addWidget(self.photo_taking)

        self.stack.setCurrentWidget(self.photo_taking)

    def handle_photo_result(self, image_path):
        """处理拍摄确认"""
        self.stack.setCurrentIndex(0)
        self.image_path = image_path
        self.start_annotation(self.image_path)

    def handle_photo_cancel(self):
        """处理拍摄取消"""
        self.stack.setCurrentIndex(0)
        QMessageBox.information(self, "提示", "已取消拍摄")

    def start_annotation(self, image_path):
        self.data_generator = Data_Generate(image_path=image_path)

        self.label_display.clear()
        defect_name = list(self.data_generator.Defect_Types.keys())[self.data_generator.current_defect]
        self.label_display.insertPlainText(f"当前的缺陷类型： {defect_name}, \nID： {self.data_generator.current_defect}")
        # self.label_display.append(f"当前的缺陷类型： {defect_name}, ID： {self.data_generator.current_defect}")

        # 读取图像
        self.data_generator.image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        self.data_generator.image = cv2.cvtColor(self.data_generator.image, cv2.COLOR_BGR2RGB)
        self.data_generator.image_copy = self.data_generator.image.copy()

        # 将 OpenCV 图像转换为 QPixmap
        height, width, channel = self.data_generator.image.shape
        bytes_per_line = 3 * width
        q_image = QImage(self.data_generator.image, width, height, bytes_per_line, QImage.Format_RGB888)
        self.pixmap = QPixmap.fromImage(q_image)

        # 让 image_label 适应图像大小
        self.image_label.setPixmap(self.pixmap)
        self.image_label.setFixedSize(width, height)

        # 启用鼠标事件进行标注（坐标相对于 QLabel，也就是图像）
        self.image_label.mousePressEvent = self.on_mouse_press
        self.image_label.mouseMoveEvent = self.on_mouse_move
        self.image_label.mouseReleaseEvent = self.on_mouse_release

        self.drawing = False  # 是否在绘制
        self.data_generator.x1, self.data_generator.x2, self.data_generator.y1, self.data_generator.y2 = -1, -1, -1, -1

    def on_mouse_press(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.data_generator.x1, self.data_generator.y1 = event.x(), event.y()

    def on_mouse_move(self, event):
        """鼠标移动事件"""
        if self.drawing:
            self.data_generator.x2, self.data_generator.y2 = event.x(), event.y()

        self.update()

    def on_mouse_release(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.LeftButton:
            self.drawing = False
            self.data_generator.x2, self.data_generator.y2 = event.x(), event.y()

            # 确保 x1, y1 是左上角，x2, y2 是右下角
            x1, y1 = (min(self.data_generator.x1, self.data_generator.x2),
                      min(self.data_generator.y1, self.data_generator.y2))
            x2, y2 = (max(self.data_generator.x1, self.data_generator.x2),
                      max(self.data_generator.y1, self.data_generator.y2))

            self.data_generator.rectangles.append((self.data_generator.current_defect, x1, y1, x2, y2))
            color = list(self.data_generator.Defect_Types.values())[self.data_generator.current_defect]
            cv2.rectangle(self.data_generator.image, (x1, y1), (x2, y2), color, 2)

            height, width, channel = self.data_generator.image.shape
            bytes_per_line = 3 * width
            q_image = QImage(self.data_generator.image, width, height, bytes_per_line, QImage.Format_RGB888)
            self.pixmap = QPixmap.fromImage(q_image)

            self.update()  # 触发绘制

    def paintEvent(self, event):
        """在 QLabel 上绘制标注框"""
        if not hasattr(self, 'pixmap') or self.pixmap is None:
            return

        temp_pixmap = self.pixmap.copy()
        painter = QPainter(temp_pixmap)

        rect_pen = QPen(Qt.red, 2)
        painter.setPen(rect_pen)

        # 绘制当前拖动的矩形
        if self.drawing:
            painter.drawRect(self.data_generator.x1, self.data_generator.y1, self.data_generator.x2 -
                             self.data_generator.x1, self.data_generator.y2 - self.data_generator.y1)

        painter.end()
        self.image_label.setPixmap(temp_pixmap)

    def save_annotations(self):
        if self.data_generator:
            save_image_path = './Annotation/images/' + self.image_path.split('/')[-1]
            save_txt_path = './Annotation/labels/' + self.image_path.split('/')[-1]
            annotated_path = self.data_generator.save_yolo_annotation(save_txt_path)
            annotated_image_path = self.data_generator.save_annotated_image(save_image_path)
            self.db.Insert_Annotation_Data(self.image_path, annotated_image_path, annotated_path)
            QMessageBox.information(self, "保存成功", "标注和图片已成功保存！")
            self.image_label.clear()
        else:
            QMessageBox.warning(self, "警告", "请先上传或拍摄图片！")

    def switch_defect(self):
        if self.data_generator:
            defect_name = self.data_generator.switch_defect()
            self.label_display.clear()
            self.label_display.insertPlainText(
                f"当前的缺陷类型： {defect_name}, \nID： {self.data_generator.current_defect}")
            # self.label_display.append(f"当前的缺陷类型： {defect_name}, ID： {self.data_generator.current_defect}")
        else:
            QMessageBox.warning(self, "警告", "请先上传或拍摄图片！")

    def return_to_main_menu(self):
        self.main_stack.setCurrentIndex(0)

    def undo_rectangle(self):
        """撤销上一个绘制的矩形"""
        if self.data_generator.rectangles:
            self.data_generator.rectangles.pop()  # 移除最后一个矩形
            self.data_generator.image = cv2.imread(self.data_generator.image_path)
            self.data_generator.image = cv2.cvtColor(self.data_generator.image, cv2.COLOR_BGR2RGB)

            # 重新绘制所有剩余的标注框
            for defect_id, x1, y1, x2, y2 in self.data_generator.rectangles:
                color = list(self.data_generator.Defect_Types.values())[defect_id]
                cv2.rectangle(self.data_generator.image, (x1, y1), (x2, y2), color, 2)

            height, width, channel = self.data_generator.image.shape
            bytes_per_line = 3 * width
            q_image = QImage(self.data_generator.image, width, height, bytes_per_line, QImage.Format_RGB888)
            self.pixmap = QPixmap.fromImage(q_image)

            self.update()  # 触发绘制

            QMessageBox.information(self, "删除成功", "已删除上一个标注框！")

        else:
            QMessageBox.warning(self, "警告", "没有可以删除的标注框！")
