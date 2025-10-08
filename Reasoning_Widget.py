import os

from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QFrame, QHBoxLayout, QDialog, QFormLayout, \
    QLineEdit, QDialogButtonBox, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt
from qfluentwidgets import HorizontalFlipView, HorizontalPipsPager, StateToolTip, PushButton, ToolButton, Flyout, \
    InfoBarIcon, InfoBar, InfoBarPosition

from Button_Style import Btn_Style
from Reasoning_Module.engine_infer import infer_parse_args, infer_main
from Reasoning_Module.train_model import train_parse_args, train_main
from Reasoning_Module.evaluation import eval_parse_args, eval_main
from DataBase_Modules.DataBase import DataBase
from qfluentwidgets import FluentIcon as FIF


class ReasoningWidget(QWidget):
    def __init__(self, main_stack):
        super().__init__()
        self.main_stack = main_stack
        self.btn_style = Btn_Style()
        self.id = []
        self.db = DataBase("localhost", "root", "123456", "new_table",
                mysql_path='/usr/bin/mysql',
                mysqldump_path='/usr/bin/mysqldump')
        self.initUI()

    def initUI(self):
        main_layout = QHBoxLayout()

        btn_layout = QVBoxLayout()
        btn_layout.setAlignment(Qt.AlignTop)

        self.stateTooltip = None

        self.btn_train = PushButton("训练")
        self.btn_eval = PushButton("评估")
        self.btn_infer = PushButton("推理")
        self.btn_visual = PushButton("可视化")
        self.btn_back = ToolButton(FIF.RETURN, self)
        self.btn_back.setToolTip('返回主界面')

        self.btn_train.clicked.connect(self.train_model)
        self.btn_eval.clicked.connect(self.eval_model)
        self.btn_infer.clicked.connect(self.infer_model)
        self.btn_visual.clicked.connect(self.visual_model)
        self.btn_back.clicked.connect(lambda: self.main_stack.setCurrentIndex(0))

        btn_layout.addWidget(self.btn_train)
        btn_layout.addWidget(self.btn_eval)
        btn_layout.addWidget(self.btn_infer)
        btn_layout.addWidget(self.btn_visual)
        btn_layout.addWidget(self.btn_back)

        self.flipView = HorizontalFlipView(self)
        self.pager = HorizontalPipsPager(self)

        pager_layout = QVBoxLayout()
        pager_layout.addWidget(self.flipView, 0, Qt.AlignCenter)
        pager_layout.addWidget(self.pager, 0, Qt.AlignCenter)
        pager_layout.setAlignment(Qt.AlignCenter)

        main_layout.addLayout(btn_layout)
        main_layout.addLayout(pager_layout)

        self.setLayout(main_layout)

    def train_model(self):
        """ 弹出一个对话框让用户输入训练参数，确认后执行训练 """

        class TrainParamDialog(QDialog):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.setWindowTitle("设置训练参数")
                self.inputs = {}
                layout = QVBoxLayout()
                form = QFormLayout()

                self.default_args = vars(train_parse_args())

                for key, val in self.default_args.items():
                    if key in ['model', 'data']:  # 需要文件选择
                        h_layout = QHBoxLayout()
                        line_edit = QLineEdit(str(val))
                        browse_btn = QPushButton("选择文件")
                        browse_btn.clicked.connect(lambda _, l=line_edit: self.select_file(l))
                        h_layout.addWidget(line_edit)
                        h_layout.addWidget(browse_btn)
                        self.inputs[key] = line_edit
                        form.addRow(f"{key}:", h_layout)
                    else:
                        line = QLineEdit(str(val))
                        self.inputs[key] = line
                        form.addRow(f"{key}:", line)

                layout.addLayout(form)
                button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
                button_box.accepted.connect(self.accept)
                button_box.rejected.connect(self.reject)
                layout.addWidget(button_box)
                self.setLayout(layout)

            def select_file(self, line_edit):
                file_path, _ = QFileDialog.getOpenFileName(self, "选择文件", "", "所有文件 (*)")
                if file_path:
                    line_edit.setText(file_path)

            def get_args(self):
                class Args:
                    pass

                args = Args()
                for key, widget in self.inputs.items():
                    val = widget.text()
                    try:
                        if val.lower() in ['true', 'false']:
                            setattr(args, key, val.lower() == 'true')
                        elif '.' in val and key not in ['model', 'data', 'name']:
                            setattr(args, key, float(val))
                        elif key in ['model', 'data', 'name']:
                            setattr(args, key, val)
                        else:
                            setattr(args, key, int(val))
                    except:
                        setattr(args, key, val)
                return args

        dialog = TrainParamDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.train_tooltip()
            try:
                args = dialog.get_args()
                train_main(args)
                self.train_tooltip()
            except Exception as e:
                self.train_tooltip(False)
                # self.result_display.setText(f"❌ 训练失败：{str(e)}")

    def eval_model(self):
        """ 弹出一个对话框让用户输入评估参数，确认后执行评估 """

        class EvalParamDialog(QDialog):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.setWindowTitle("设置评估参数")
                self.inputs = {}
                layout = QVBoxLayout()
                form = QFormLayout()

                self.default_args = vars(eval_parse_args())

                for key, val in self.default_args.items():
                    if key in ['model', 'yaml']:
                        h_layout = QHBoxLayout()
                        line_edit = QLineEdit(str(val))
                        browse_btn = QPushButton("选择文件")
                        browse_btn.clicked.connect(lambda _, l=line_edit: self.select_file(l))
                        h_layout.addWidget(line_edit)
                        h_layout.addWidget(browse_btn)
                        self.inputs[key] = line_edit
                        form.addRow(f"{key}:", h_layout)
                    else:
                        line = QLineEdit(str(val))
                        self.inputs[key] = line
                        form.addRow(f"{key}:", line)

                layout.addLayout(form)
                button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
                button_box.accepted.connect(self.accept)
                button_box.rejected.connect(self.reject)
                layout.addWidget(button_box)
                self.setLayout(layout)

            def select_file(self, line_edit):
                file_path, _ = QFileDialog.getOpenFileName(self, "选择文件", "", "所有文件 (*)")
                if file_path:
                    line_edit.setText(file_path)

            def get_args(self):
                class Args:
                    pass

                args = Args()
                for key, widget in self.inputs.items():
                    val = widget.text()
                    try:
                        if val.lower() in ['true', 'false']:
                            setattr(args, key, val.lower() == 'true')
                        elif '.' in val and key not in ['model', 'yaml', 'name', 'task']:
                            setattr(args, key, float(val))
                        elif key in ['model', 'yaml', 'name', 'task']:
                            setattr(args, key, val)
                        else:
                            setattr(args, key, int(val))
                    except:
                        setattr(args, key, val)
                return args

        dialog = EvalParamDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.eval_tooltip()
            try:
                args = dialog.get_args()
                mp50 = eval_main(args)
                
                self.show_eval(mp50)
                self.eval_tooltip()
            except Exception as e:
                print(e)
                self.eval_tooltip(False)

    def show_eval(self, mp50):
        InfoBar.success(
            title='评估成功',
            content=f"mAP = {mp50}",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            # position='Custom', # NOTE: use custom info bar manager
            duration=6000,
            parent=self
            )

    def infer_model(self):
        """ 弹出一个对话框让用户输入推理参数，确认后执行推理 """

        class ParamDialog(QDialog):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.setWindowTitle("设置推理参数")
                self.inputs = {}
                layout = QVBoxLayout()
                form = QFormLayout()

                self.default_args = vars(infer_parse_args())

                for key, val in self.default_args.items():
                    if key in ['model', 'img_path', 'img_dir']:
                        # 用带选择按钮的路径输入框
                        h_layout = QHBoxLayout()
                        line_edit = QLineEdit(str(val))
                        browse_btn = QPushButton("选择")

                        if key == 'img_dir':
                            browse_btn.clicked.connect(lambda _, l=line_edit: self.select_folder(l))
                        else:
                            browse_btn.clicked.connect(lambda _, l=line_edit: self.select_file(l))

                        h_layout.addWidget(line_edit)
                        h_layout.addWidget(browse_btn)
                        self.inputs[key] = line_edit
                        form.addRow(f"{key}:", h_layout)
                    else:
                        # 其他普通参数
                        line = QLineEdit(str(val))
                        self.inputs[key] = line
                        form.addRow(f"{key}:", line)

                layout.addLayout(form)

                button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
                button_box.accepted.connect(self.accept)
                button_box.rejected.connect(self.reject)
                layout.addWidget(button_box)
                self.setLayout(layout)

            def select_file(self, line_edit):
                file_path, _ = QFileDialog.getOpenFileName(self, "选择文件", "", "所有文件 (*)")
                if file_path:
                    line_edit.setText(file_path)

            def select_folder(self, line_edit):
                folder_path = QFileDialog.getExistingDirectory(self, "选择文件夹", "")
                if folder_path:
                    line_edit.setText(folder_path)

            def get_args(self):
                class Args:
                    pass

                args = Args()
                for key, widget in self.inputs.items():
                    val = widget.text()
                    try:
                        if val.lower() in ['true', 'false']:
                            setattr(args, key, val.lower() == 'true')
                        elif key in ['img_path', 'img_dir'] and val is None:
                            setattr(args, key, None)
                        elif key in ['img_path', 'img_dir'] and val == "None":
                            setattr(args, key, None)
                        elif '.' in val and key not in ['model', 'img_path', 'img_dir', 'save_path', 'hard_dir']:
                            setattr(args, key, float(val))
                        elif key in ['model', 'img_path', 'img_dir', 'save_path', 'hard_dir'] and val != "None":
                            setattr(args, key, val)
                        else:
                            setattr(args, key, int(val))
                    except:
                        setattr(args, key, val)
                return args

        dialog = ParamDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.infer_tooltip()
            args = dialog.get_args()
            try:
                result_paths = infer_main(args)

                img_path_list = []
                if args.img_path is not None:
                    img_path_list = [i for i in args.img_path.split(',')]
                elif args.img_dir is not None:
                    img_path_list = [os.path.join(args.img_dir, i)
                                     for i in os.listdir(args.img_dir)]
                for img_path, result_path in zip(img_path_list, result_paths):
                    img_path = img_path.replace('\\', '/')
                    result_path = result_path.replace('\\', '/')
                    self.db.Insert_Detected_Image_Data(img_path, result_path)
                    txt_path = os.path.join(args.save_path, img_path.split('/')[-1].split('.')[0] + '.txt')
                    img_name = img_path.split('/')[-1].split('\\')[-1]
                    id = self.db.get_image_id([img_path.split('/')[-1]])
                    self.id.append(id[0])
                    self.db.Insert_Detected_Details(id[0], img_name, txt_path)

                self.clear_flip_view()
                self.flipView.addImages(result_paths)
                self.pager.setPageNumber(self.flipView.count())
                self.pager.currentIndexChanged.connect(self.flipView.setCurrentIndex)
                self.flipView.currentIndexChanged.connect(self.pager.setCurrentIndex)
                self.infer_tooltip()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"推理失败：{str(e)}")
                self.infer_tooltip(False)

    def visual_model(self):
        visual_paths = self.db.Defect_Result_Visualize(self.id)
        self.clear_flip_view()
        self.flipView.addImages(visual_paths)
        self.pager.setPageNumber(self.flipView.count())
        self.pager.currentIndexChanged.connect(self.flipView.setCurrentIndex)
        self.flipView.currentIndexChanged.connect(self.pager.setCurrentIndex)

    def train_tooltip(self, flag=True):
        if self.stateTooltip and flag == False:
            self.stateTooltip.setContent('模型训练失败')
            self.stateTooltip.setState(True)
            self.stateTooltip = None
        elif self.stateTooltip:
            self.stateTooltip.setContent('模型训练完成啦 😆')
            self.stateTooltip.setState(True)
            self.stateTooltip = None
        else:
            self.stateTooltip = StateToolTip('正在训练模型', '客官请耐心等待哦~~', self)
            self.stateTooltip.move(420, 30)
            self.stateTooltip.show()
            self.repaint()

    def eval_tooltip(self, flag=True):
        if self.stateTooltip and flag == False:
            self.stateTooltip.setContent('模型评价失败')
            self.stateTooltip.setState(True)
            self.stateTooltip = None
        elif self.stateTooltip:
            self.stateTooltip.setContent('模型评价完成啦 😆')
            self.stateTooltip.setState(True)
            self.stateTooltip = None
        else:
            self.stateTooltip = StateToolTip('正在评价模型', '客官请耐心等待哦~~', self)
            self.stateTooltip.move(420, 30)
            self.stateTooltip.show()
            self.repaint()

    def infer_tooltip(self, flag=True):
        if self.stateTooltip and flag == False:
            self.stateTooltip.setContent('模型推理失败')
            self.stateTooltip.setState(True)
            self.stateTooltip = None
        elif self.stateTooltip:
            self.stateTooltip.setContent('模型推理完成啦 😆')
            self.stateTooltip.setState(True)
            self.stateTooltip = None
        else:
            self.stateTooltip = StateToolTip('正在推理模型', '客官请耐心等待哦~~', self)
            self.stateTooltip.move(420, 30)
            self.stateTooltip.show()
            self.repaint()

    def clear_flip_view(self):
        self.flipView.clear()
        self.pager.clear()