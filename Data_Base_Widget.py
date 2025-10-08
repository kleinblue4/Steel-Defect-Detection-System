from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QVBoxLayout, QLabel, QStackedWidget, \
    QHBoxLayout, QFileDialog, QMessageBox, QTableWidgetItem, QAbstractItemView, QTableWidget, QComboBox, QInputDialog
from PyQt5.QtCore import Qt
from qfluentwidgets import TableWidget, ComboBox, TransparentToolButton, PushButton, TitleLabel, BodyLabel, \
    StrongBodyLabel, \
    SubtitleLabel
from qfluentwidgets import FluentIcon as FIF
from DataBase_Modules.DataBase import DataBase
from Button_Style import Btn_Style


class DataBaseWidget(QWidget):
    def __init__(self, stack):
        super().__init__()
        self.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.db = DataBase("localhost", "root", "123456", "new_table",
                mysql_path='/usr/bin/mysql',
                mysqldump_path='/usr/bin/mysqldump')
        self.stack = stack
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()

        layout = QHBoxLayout()

        # 标题
        title_label = SubtitleLabel("数据库管理")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("background-color: rgba(255, 255, 255, 0)")
        # title_label.setStyleSheet("font-size: 24px; font-weight: bold; padding: 10px;")
        main_layout.addWidget(title_label)

        # **添加表选择下拉框**
        self.table_selector = ComboBox(self)
        self.table_selector.addItems(
            ["Detection_results", "Annotation_data", "Detection_reports", "Defect_details"])
        self.table_selector.setFixedWidth(300)
        self.table_selector.setFixedHeight(40)
        self.table_selector.currentIndexChanged.connect(self.query_data)
        # 按钮布局
        btn_layout = QVBoxLayout()

        # 重连数据库按钮
        self.reconnect_btn = TransparentToolButton(FIF.UPDATE, self)
        self.reconnect_btn.setToolTip("重连数据库")
        self.reconnect_btn.clicked.connect(self.reconnect_database)
        btn_layout.addWidget(self.reconnect_btn)

        # 插入数据按钮
        self.insert_btn = TransparentToolButton(FIF.ADD, self)
        self.insert_btn.setToolTip("插入数据")
        self.insert_btn.clicked.connect(self.insert_data)
        btn_layout.addWidget(self.insert_btn)

        # 备份数据库按钮
        self.backup_btn = TransparentToolButton(FIF.CLOUD, self)
        self.backup_btn.setToolTip("备份数据库")
        self.backup_btn.clicked.connect(self.backup_database)
        btn_layout.addWidget(self.backup_btn)

        # 恢复数据库按钮
        self.restore_btn = TransparentToolButton(FIF.CLOUD_DOWNLOAD, self)
        self.restore_btn.setToolTip("恢复数据库")
        self.restore_btn.clicked.connect(self.restore_database)
        btn_layout.addWidget(self.restore_btn)

        self.query_btn = TransparentToolButton(FIF.SEARCH, self)
        self.query_btn.setToolTip("查询数据")
        self.query_btn.clicked.connect(self.query_data)
        btn_layout.addWidget(self.query_btn)

        self.delete_btn = TransparentToolButton(FIF.DELETE, self)
        self.delete_btn.setToolTip("删除数据")
        self.delete_btn.clicked.connect(self.delete_data)
        btn_layout.addWidget(self.delete_btn)

        self.download_btn = TransparentToolButton(FIF.DOWNLOAD, self)
        self.download_btn.setToolTip("下载数据")
        self.download_btn.clicked.connect(self.download_selected_images)
        btn_layout.addWidget(self.download_btn)

        self.return_button = TransparentToolButton(FIF.RETURN, self)
        self.return_button.setToolTip("返回主界面")
        self.return_button.clicked.connect(self.return_to_main_menu)
        btn_layout.addWidget(self.return_button)

        btn_layout.addStretch()

        layout.addLayout(btn_layout)
        right_layout = QVBoxLayout()
        right_layout.addWidget(self.table_selector)
        # **表格控件**
        self.table_widget = TableWidget(self)
        self.table_widget.setBorderVisible(True)
        self.table_widget.setBorderRadius(8)
        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 禁止编辑
        right_layout.addWidget(self.table_widget)
        layout.addLayout(right_layout)
        main_layout.addLayout(layout)

        self.setLayout(main_layout)

    def reconnect_database(self):
        is_success_reconnect, e = self.db.Reconnect_Database()
        if is_success_reconnect:
            QMessageBox.information(self, "重连成功", "数据库已重新连接！")
        else:
            QMessageBox.information(self, "重连失败", "无法重新连接到数据库！")

    def query_data(self):
        table_name = self.table_selector.currentText()
        print(f"正在查询表: {table_name}")
        try:
            data = self.db.Query_Table_Data(table_name)
            print(f"查询结果: {data}")
            if table_name == "Detection_results":
                headers = ["ID", "图片名称", "图片类型", "上传时间"]
                col_indices = [0, 1, 2, 3]
            elif table_name == "Annotation_data":
                headers = ["ID", "图片名称", "图片类型", "上传时间"]
                col_indices = [0, 1, 2, 3]
            elif table_name == "Detection_reports":
                headers = ["ID", "报告文件名", "文件类型", "上传时间"]
                col_indices = [0, 1, 2, 3]
            elif table_name == "Defect_details":
                headers = ["ID", "图片名称", "结果图像ID", "缺陷类型", "X坐标", "Y坐标", "图像宽度", "图像高度",
                           "缺陷区域占比"]
                col_indices = [0, 1, 2, 3, 4, 5, 6, 7, 8]
            else:
                return

            self.table_widget.setColumnCount(len(headers))
            self.table_widget.setHorizontalHeaderLabels(headers)
            self.table_widget.setRowCount(len(data))

            for row_idx, row_data in enumerate(data):
                for col_idx, col_value in enumerate(col_indices):
                    self.table_widget.setItem(row_idx, col_idx, QTableWidgetItem(str(row_data[col_value])))

        except Exception as e:
            QMessageBox.critical(self, "查询错误", f"查询数据失败: {e}")

    def delete_data(self):
        """删除选中的数据库记录"""
        selected_rows = sorted(set(index.row() for index in self.table_widget.selectedIndexes()), reverse=True)
        if not selected_rows:
            QMessageBox.warning(self, "删除失败", "请选择要删除的数据行！")
            return

        confirm = QMessageBox.question(self, "确认删除", f"确定要删除 {len(selected_rows)} 条数据吗？",
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if confirm == QMessageBox.Yes:
            try:
                delete_id = []
                for row in selected_rows:
                    record_id = self.table_widget.item(row, 0).text()
                    delete_id.append(record_id)
                table_name = self.table_selector.currentText()
                if table_name == "Detection_results":
                    self.db.Delete_Detected_Image_Data(delete_id)  # 删除数据库记录
                elif table_name == "Annotation_data":
                    self.db.Delete_Annotation_Data(delete_id)
                elif table_name == "Detection_reports":
                    self.db.Delete_Detection_Report(delete_id)
                elif table_name == "Defect_details":
                    self.db.Delete_Defect_Details(delete_id)
                self.query_data()
                print("成功删除数据", delete_id)
                QMessageBox.information(self, "删除成功", "选中数据已删除！")
            except Exception as e:
                QMessageBox.critical(self, "删除错误", f"删除数据失败: {e}")

    def download_selected_images(self):
        """下载"""

        selected_rows = sorted(set(index.row() for index in self.table_widget.selectedIndexes()), reverse=True)
        selected_ids = []
        for row in selected_rows:
            record_id = self.table_widget.item(row, 0).text()
            selected_ids.append(record_id)

        if not selected_ids:
            QMessageBox.warning(self, "未选择数据", "请选择要下载的数据！")
            return

        save_path = QFileDialog.getExistingDirectory(self, "选择保存路径")
        if not save_path:
            return

        try:
            table_name = self.table_selector.currentText()
            if table_name == "Detection_results":
                self.db.Get_Detected_Image(selected_ids, save_path)
                QMessageBox.information(self, "下载成功", "图片已成功下载！")
            elif table_name == "Annotation_data":
                self.db.Get_Annotation_Data(selected_ids, save_path)
                QMessageBox.information(self, "下载成功", "标注数据已成功下载！")
            elif table_name == "Detection_reports":
                self.db.Get_Report_File(selected_ids, save_path)
                QMessageBox.information(self, "下载成功", "检测报告已成功下载！")
            elif table_name == "Defect_details":
                self.db.Get_Defect_Details(selected_ids, save_path)
                QMessageBox.information(self, "下载成功", "详细检测结果已成功下载！")

        except Exception as e:
            QMessageBox.critical(self, "下载错误", f"下载失败: {e}")
    

    def return_to_main_menu(self):
        self.db.Release_Database()
        self.stack.setCurrentIndex(0)  # 切换回主菜单

    def insert_data(self):
        """使用文件选择和输入对话框来收集插入数据所需参数，并调用数据库插入方法"""
        table_name = self.table_selector.currentText()

        try:
            if table_name == "Detection_results":
                # 选择检测结果图片
                image_path, _ = QFileDialog.getOpenFileName(self, "选择检测结果图片", "",
                                                            "Images (*.png *.jpg *.bmp);;All Files (*)")
                if not image_path:
                    return

                # 选择缺陷标注图片
                defect_mask_path, _ = QFileDialog.getOpenFileName(self, "选择缺陷标注图片", "",
                                                                  "Images (*.png *.jpg *.bmp);;All Files (*)")
                if not defect_mask_path:
                    return

                self.db.Insert_Detected_Image_Data(image_path, defect_mask_path)
                image_name = image_path.split("/")[-1]
                image_id = self.db.get_image_id([image_name])
                QMessageBox.information(self, "插入成功", f"图片数据 {image_path.split('/')[-1]} 插入成功！")
                self.query_data()

            elif table_name == "Annotation_data":
                # 选择检测结果图片
                image_path, _ = QFileDialog.getOpenFileName(self, "选择检测结果图片", "",
                                                            "Images (*.png *.jpg *.bmp);;All Files (*)")
                if not image_path:
                    return

                # 选择缺陷掩码图片
                defect_mask_path, _ = QFileDialog.getOpenFileName(self, "选择缺陷掩码图片", "",
                                                                  "Images (*.png *.jpg *.bmp);;All Files (*)")
                if not defect_mask_path:
                    return

                # 选择缺陷信息
                yolo_anno_path, _ = QFileDialog.getOpenFileName(self, "选择缺陷信息（txt文件）", "",
                                                                "txt (*.txt);;All Files (*)")
                if not yolo_anno_path:
                    return

                self.db.Insert_Annotation_Data(image_path, defect_mask_path, yolo_anno_path)
                QMessageBox.information(self, "插入成功", f"标注图片数据 {image_path.split('/')[-1]} 插入成功！")
                self.query_data()

            elif table_name == "Detection_reports":
                # 选择检测结果图片
                report_path, _ = QFileDialog.getOpenFileName(self, "选择报告文件", "",
                                                             "Report (*.pdf *.doc *.docx);;All Files (*.*)")
                if not report_path:
                    return

                self.db.Insert_Detected_Image_Data(report_path)
                QMessageBox.information(self, "插入成功", f"报告文件数据 {report_path.split('/')[-1]} 插入成功！")
                self.query_data()

        except Exception as e:
            QMessageBox.critical(self, "错误", f"插入数据时发生错误: {e}")

    def backup_database(self):
        """备份数据库"""
        backup_file, _ = QFileDialog.getSaveFileName(self, "选择备份文件", "", "SQL 文件 (*.sql)")
        if backup_file:
            try:
                self.db.Backup_DataBase(backup_file)
                QMessageBox.information(self, "备份成功", f"数据库已备份到: {backup_file}\n")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"备份失败: {str(e)}")

    def restore_database(self):
        """恢复数据库"""
        backup_file, _ = QFileDialog.getOpenFileName(self, "选择备份文件", "", "SQL 文件 (*.sql)")
        if backup_file:
            try:
                self.db.Restore_Database(backup_file)
                QMessageBox.information(self, "恢复成功", f"数据库已从 {backup_file} 恢复\n")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"恢复失败: {str(e)}")
