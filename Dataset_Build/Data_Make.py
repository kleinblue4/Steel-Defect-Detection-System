import cv2
import numpy as np
import os
# from ..DataBase_Modules.DataBase import DataBase
from Dataset_Build.DEFECT_TYPE import DEFECT_TYPES


class Data_Generate():
    def __init__(self, image_path=None, txt_path=None):
        # 对四种缺陷的标注设置颜色
        self.Defect_Types = DEFECT_TYPES

        self.rectangles = []
        self.drawing = False  # 是否在绘制
        self.current_defect = 0  # 当前的缺陷类型
        self.x1, self.y1, self.x2, self.y2 = -1, -1, -1, -1  # 记录标注缺陷的上一个像素点，从而与当前的像素点连接起来
        self.image_path = image_path  # 所要标注的图片的路径
        self.image = None  # 输入的所要标注的图片
        self.image_copy = None  # 用于刷新绘制的图片
        if txt_path is None:
            txt_path = self.image_path.split('/')[-1].split('.')[0] + "_anno.txt"
        self.txt_path = txt_path

        self.ensure_file_exists(self.txt_path)  # 首先确保csv文件存在，不存在则创建

    # 确保保存数据的txt文件存在
    def ensure_file_exists(self, file_path):
        """ 检查文件是否存在 """
        if not os.path.exists(file_path):
            with open(file_path, 'w') as file:
                file.write("")
            print(f"文件 {file_path} 已创建")
        else:
            print(f"文件 {file_path} 已存在")

    # ''' 使用鼠标绘制缺陷区域 '''
    def draw_rectangle(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.x1 = x
            self.y1 = y
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing:
                self.image_copy = self.image.copy()
                color = list(self.Defect_Types.values())[self.current_defect]
                cv2.rectangle(self.image_copy, (self.x1, self.y1), (x, y), color, 2)
                cv2.imshow("Image", self.image_copy)
        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
            self.x2 = x
            self.y2 = y
            if self.x1 != self.x2 and self.y1 != self.y2:
                self.rectangles.append((self.current_defect, self.x1, self.y1, self.x2, self.y2))
                color = list(self.Defect_Types.values())[self.current_defect]
                cv2.rectangle(self.image, (self.x1, self.y1), (self.x2, self.y2), color, 2)
                cv2.imshow("Image", self.image)

    def save_yolo_annotation(self, image_path):
        height, width, _ = self.image.shape
        annotation_data = []

        for defect_id, x1, y1, x2, y2 in self.rectangles:
            # 计算归一化坐标
            x_min, x_max = min(x1, x2), max(x1, x2)
            y_min, y_max = min(y1, y2), max(y1, y2)

            x_center = (x_min + x_max) / 2.0 / width
            y_center = (y_min + y_max) / 2.0 / height
            w_norm = (x_max - x_min) / width
            h_norm = (y_max - y_min) / height

            annotation_data.append(f"{defect_id} {x_center:.6f} {y_center:.6f} {w_norm:.6f} {h_norm:.6f}")

        if annotation_data:
            txt_filename = os.path.splitext(image_path)[0] + "_anno.txt"
            with open(txt_filename, "w") as f:
                f.write("\n".join(annotation_data))
            print(f"YOLO 标注已保存: {txt_filename}")
            return txt_filename

    # 转换所要标注的缺陷
    def switch_defect(self):
        self.current_defect = (self.current_defect + 1) % len(self.Defect_Types)
        defect_name = list(self.Defect_Types.keys())[self.current_defect]
        print(f"当前的缺陷类型： {defect_name}, ID： {self.current_defect}")
        return defect_name

    def save_annotated_image(self, image_path):
        self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        # annotated_image_path = os.path.splitext(image_path)[0] + "_annotated.png"
        cv2.imwrite(image_path, self.image)
        print(f"带有边界框的图片已保存: {image_path}")
        return image_path

    def undo_last_annotation(self):
        if self.rectangles:
            # 删除最后一个标注框
            self.rectangles.pop()

            # 重新加载原始图像
            self.image = cv2.imread(self.image_path)

            # 重新绘制所有剩余的标注框
            for defect_id, x1, y1, x2, y2 in self.rectangles:
                color = list(self.Defect_Types.values())[defect_id]
                cv2.rectangle(self.image, (x1, y1), (x2, y2), color, 2)

            # 显示更新后的图片
            self.image_copy = self.image
            print("已删除上一个标注框")
        else:
            print("没有可以删除的标注框")

    def main(self):

        self.image = cv2.imread(self.image_path)

        if self.image is None:
            print('错误：无法加载图片！请检查路径。')
            return
        self.image_copy = self.image.copy()

        cv2.namedWindow("Image")
        cv2.setMouseCallback("Image", self.draw_rectangle)

        print("按 's' 保存 YOLO 标注和带有边界框的图片, 'c' 切换缺陷类型, 'q' 退出")

        while True:
            cv2.imshow("Image", self.image_copy)
            key = cv2.waitKey(1) & 0xFF

            if key == ord("s"):  # 按 's' 保存数据
                self.save_yolo_annotation(image_path=self.image_path)
                self.save_annotated_image(image_path=self.image_path)
            elif key == ord("c"):  # 按 'c' 切换缺陷类型
                self.switch_defect()
            elif key == ord("q"):  # 按 'q' 退出
                break

        cv2.destroyAllWindows()


if __name__ == "__main__":
    data_generate = Data_Generate(image_path="123.png")
    data_generate.main()
