from PyQt5.QtWidgets import QPushButton, QWidget, QVBoxLayout, \
    QHBoxLayout, QTextEdit, QLineEdit, QFileDialog, QMessageBox, QInputDialog
from qfluentwidgets import ToolButton, SearchLineEdit, TextBrowser
from qfluentwidgets import FluentIcon as FIF
from Chat_Module.AI_Report import Kimi_Chat
from Button_Style import Btn_Style
from DataBase_Modules.DataBase import DataBase


class KimiChatWidget(QWidget):
    def __init__(self, stack):
        super().__init__()
        self.setStyleSheet("background-color: rgb(255, 255, 255);")
        # 初始化 Kimi_Chat
        self.kimi = Kimi_Chat(md_path='chat_history.md')
        self.stack = stack
        self.txt = ''
        # 创建界面组件
        self.init_ui()

    def init_ui(self):
        # 创建主水平布局
        main_layout = QHBoxLayout()

        # 左侧按钮垂直布局
        button_layout = QVBoxLayout()

        self.btn_style = Btn_Style()

        self.send_button = ToolButton(FIF.SEND, self)
        self.send_button.setToolTip('发送')
        self.send_button.clicked.connect(self.send_message)
        button_layout.addWidget(self.send_button)

        self.report_button = ToolButton(FIF.DOCUMENT, self)
        self.report_button.setToolTip('生成报告')
        self.report_button.clicked.connect(self.generate_report)
        button_layout.addWidget(self.report_button)

        self.clear_button = ToolButton(FIF.CLOSE, self)
        self.clear_button.setToolTip('清空聊天记录')
        self.clear_button.clicked.connect(self.clear_chat)
        button_layout.addWidget(self.clear_button)

        self.save_button = ToolButton(FIF.SAVE, self)
        self.save_button.setToolTip('保存聊天记录')
        self.save_button.clicked.connect(self.save_chat)
        button_layout.addWidget(self.save_button)

        self.return_button = ToolButton(FIF.RETURN, self)
        self.return_button.setToolTip('返回主界面')
        self.return_button.clicked.connect(self.return_to_main_menu)
        button_layout.addWidget(self.return_button)

        # 占位符扩展，保证按钮靠上
        button_layout.addStretch()

        # 右侧聊天区域
        chat_layout = QVBoxLayout()

        # 聊天记录框
        self.chat_display = TextBrowser(self)
        self.chat_display.setReadOnly(True)  # 只读
        chat_layout.addWidget(self.chat_display)

        # 用户输入框
        self.input_box = SearchLineEdit()
        self.input_box.searchSignal.connect(self.send_message)
        self.input_box.setPlaceholderText("输入你的问题...")
        self.input_box.returnPressed.connect(self.send_message)  # 绑定回车键发送消息
        chat_layout.addWidget(self.input_box)

        # 添加左右布局到主布局
        main_layout.addLayout(button_layout, 1)  # 按钮区域，权重 1
        main_layout.addLayout(chat_layout, 3)  # 聊天区域，权重 3

        # 设置窗口布局
        self.setLayout(main_layout)
        self.setWindowTitle("Kimi AI Chat")
        self.resize(600, 400)

    def return_to_main_menu(self):
        self.stack.setCurrentIndex(0)

    def generate_report(self):
        # 从数据库中提取检测结果
        try:
            db = DataBase("localhost", "root", "123456", "new_table",
                mysql_path='/usr/bin/mysql',
                mysqldump_path='/usr/bin/mysqldump')
            infer_list, ok = QInputDialog.getText(self, "生成报告", "请输入要生成报告的id列表（如[1,2,3,4]）：")
            if ok:
                import ast
                infer_list = ast.literal_eval(infer_list)
            else :
                infer_list =  [i for i in range(53, 74)]
            results = db.Infer_Result_Extra(infer_list)
            if results is None:
                QMessageBox.critical(self, "数据库错误", "数据库查询出错")
                return
        except Exception as e:
            QMessageBox.critical(self, "数据库错误", f"数据库连接失败或查询出错：{e}")
            return

        # 获取用户输入信息
        utils_msg, ok1 = QInputDialog.getText(self, "设备信息", "请输入生产环境的设备信息（若无输入-1）：")
        utils_msg = utils_msg if ok1 else "-1"

        product_msg, ok2 = QInputDialog.getText(self, "产品信息", "请输入生产过程的产品信息（若无输入-1）：")
        product_msg = product_msg if ok2 else "-1"

        staff_msg, ok3 = QInputDialog.getText(self, "人员信息", "请输入生产过程的人员信息（若无输入-1）：")
        staff_msg = staff_msg if ok3 else "-1"

        craft_msg, ok4 = QInputDialog.getText(self, "工艺信息", "请输入生产过程的工艺信息（若无输入-1）：")
        craft_msg = craft_msg if ok4 else "-1"

        info_dict = {
            "生产环境的设备信息": utils_msg,
            "生产过程的产品信息": product_msg,
            "生产过程的人员信息": staff_msg,
            "生产过程的工艺信息": craft_msg
        }
        filtered_info = {key: value for key, value in info_dict.items() if value != '-1'}
        additional_info = "\n".join([f"- **{key}**: {value}" for key, value in filtered_info.items()]) or "无"

        # 构建 Prompt
        prompt = \
            f"""
                # 缺陷检测报告生成任务
        
                ## 背景信息
                你正在为一个缺陷检测任务生成一份专业的检测报告。以下是本次检测任务中提取的关键数据，请根据这些数据生成一份详细的分析报告。
        
                ## 检测结果数据
                以下是本次缺陷检测任务中提取的核心信息：
                - **缺陷类型**: {results[0]}  
                  （检测到的缺陷种类及其分类结果）
        
                - **每种缺陷出现的次数**: {results[1]}  
                  （每种缺陷在检测样本中的出现频次）
        
                - **每种缺陷归一化后的中心点平均位置**: {results[2]}  
                  （每种缺陷区域的几何中心点在图像中的归一化坐标平均值，范围为 [0, 1]）
        
                - **每种缺陷区域归一化后的平均长和宽**: {results[3]}  
                  （每种缺陷区域的边界框在图像中的归一化宽度和高度平均值，范围为 [0, 1]）
        
                - **每种缺陷中心点的标准差**: {results[4]}  
                  （每种缺陷中心点分布的标准差，用于衡量中心点位置的离散程度）
        
                - **每种缺陷的平均面积占比 (缺陷面积 / 图片面积)**: {results[5]}  
                  （每种缺陷区域面积占整张图像面积的比例，范围为 [0, 1])
        
                - **每种缺陷的面积标准差**: {results[6]}  
                  （每种缺陷面积占比的标准差，用于衡量每种面积分布的离散程度）
        
                - **不同时间段内缺陷的出现情况**: {results[7]}  
                  （缺陷在不同时间段内的出现频率）
        
                ## 其他信息
                {additional_info}
        
                ## 报告要求
                请根据上述数据完成以下任务：
                1. **数据分析与总结**:
                   - 分析每种缺陷的分布特点（如位置、大小、面积占比等）。
                   - 对比不同时间段内的缺陷分布情况，分析是否存在时间上的规律性。
                   - 总结缺陷的主要特征及其可能的原因。
        
                2. **改进建议**:
                   - 基于以上的数据，提供详细的改进建议，包括但不限于：对生产设备的使用与维护、产品的改进、人员培训、工艺改良等。（要求每条建议不少于150字）
        
                3. **总结与结论**:
                   - 根据以上的所有信息与分析结果，进行归纳和总结，为现实场景中的生产和决策提供优化建议。
        
                ## 格式要求
                   - 对于缺陷检测报告，请你严格根据以下的格式来输出报告内容：
                   # 缺陷检测报告
                   ## 1. 数据分析与总结
                   ### 1.1 缺陷分布特点分析
                   ## 1.1.1 位置分布
            """

        # 使用 Kimi 生成报告
        try:
            report_text = self.kimi.chat(prompt)
            self.kimi.convert_to_pdf(pdf_file='new.pdf')
            self.chat_display.setMarkdown(f"**Kimi:** \n{report_text}\n")
        except Exception as e:
            QMessageBox.critical(self, "Kimi 错误", f"生成报告失败：{e}")

    def send_message(self):
        """ 处理用户输入并与 Kimi 交互 """
        user_input = self.input_box.text().strip()
        if not user_input:
            return
        ai_response = self.kimi.chat(user_input)
        # 获取当前内容
        current_text = self.chat_display.toMarkdown()  # 需要 Qt 5.14+
        new_text = f"{current_text}\n**你:** {user_input}\n\n**Kimi:** {ai_response}\n"

        # 更新全部内容
        self.chat_display.setMarkdown(new_text)
        self.input_box.clear()

    def upload_files(self):
        """ 处理上传文件 """
        file_paths, _ = QFileDialog.getOpenFileNames(self, "选择文件")
        if not file_paths:
            return

        question = "请分析上传的文件内容"
        response = self.kimi.chat_with_files(question, file_paths)

        self.chat_display.append("**你:** 上传了文件\n")
        self.chat_display.append(f"**Kimi:** {response}\n")

    def clear_chat(self):
        """ 清空聊天记录 """
        self.chat_display.clear()
        self.kimi.clear_message()

    def save_chat(self):
        """ 保存聊天记录到 Markdown 或 PDF """
        options = ["Markdown 文件 (*.md)", "PDF 文件 (*.pdf)"]
        file_path, selected_filter = QFileDialog.getSaveFileName(self, "保存聊天记录", "", ";;".join(options))

        if file_path:
            if selected_filter == options[0]:  # Markdown
                self.kimi.md_path = file_path
                self.kimi.save_to_markdown()
            elif selected_filter == options[1]:  # PDF
                self.kimi.convert_to_pdf(file_path)

            QMessageBox.information(self, "保存成功", f"聊天记录已保存到 {file_path}")
