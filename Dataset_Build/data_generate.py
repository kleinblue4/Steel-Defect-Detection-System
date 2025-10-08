import numpy as np
import os
from DEFECT_TYPE import DEFECT_TYPES
import cv2

current_defect = 0  # 当前缺陷类别索引
rectangles = []  # 存储标注框信息
drawing = False
x1, y1, x2, y2 = -1, -1, -1, -1  # 记录拖拽的坐标
image = None
image_copy = None  # 用于刷新绘制的图片

def draw_rectangle(event, x, y, flags, param):
    """鼠标拖拽绘制矩形"""
    global drawing, x1, y1, x2, y2, image_copy, image

    if event == cv2.EVENT_LBUTTONDOWN:  # 按下鼠标左键，记录起点
        drawing = True
        x1, y1 = x, y

    elif event == cv2.EVENT_MOUSEMOVE:  # 移动鼠标，实时显示矩形
        if drawing:
            image_copy = image.copy()
            color = list(DEFECT_TYPES.values())[current_defect]  # 获取当前颜色
            cv2.rectangle(image_copy, (x1, y1), (x, y), color, 2)  # 画矩形框
            cv2.imshow("Image", image_copy)

    elif event == cv2.EVENT_LBUTTONUP:  # 释放鼠标左键，记录终点
        drawing = False
        x2, y2 = x, y
        if x1 != x2 and y1 != y2:  # 确保框大小有效
            rectangles.append((current_defect, x1, y1, x2, y2))
            color = list(DEFECT_TYPES.values())[current_defect]  # 获取当前颜色
            cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)  # 画最终的框
            cv2.imshow("Image", image)

def save_yolo_annotation(image_path):
    """保存 YOLO 格式标注"""
    height, width, _ = image.shape
    annotation_data = []

    for defect_id, x1, y1, x2, y2 in rectangles:
        # 计算归一化坐标
        x_min, x_max = min(x1, x2), max(x1, x2)
        y_min, y_max = min(y1, y2), max(y1, y2)

        x_center = (x_min + x_max) / 2.0 / width
        y_center = (y_min + y_max) / 2.0 / height
        w_norm = (x_max - x_min) / width
        h_norm = (y_max - y_min) / height

        annotation_data.append(f"{defect_id} {x_center:.6f} {y_center:.6f} {w_norm:.6f} {h_norm:.6f}")

    # 保存为 .txt 文件
    if annotation_data:
        txt_filename = os.path.splitext(image_path)[0] + "_anno.txt"
        with open(txt_filename, "w") as f:
            f.write("\n".join(annotation_data))
        print(f"YOLO 标注已保存: {txt_filename}")

def switch_defect():
    """切换缺陷类型，更新颜色"""
    global current_defect
    current_defect = (current_defect + 1) % len(DEFECT_TYPES)
    defect_name = list(DEFECT_TYPES.keys())[current_defect]
    print(f"当前缺陷类型: {defect_name} (ID: {current_defect})")

def save_annotated_image(image_path):
    """保存带有边界框的图片"""
    annotated_image_path = os.path.splitext(image_path)[0] + "_annotated.png"
    cv2.imwrite(annotated_image_path, image)
    print(f"带有边界框的图片已保存: {annotated_image_path}")

def main(image_path):
    """主函数 - 载入图片并进行标注"""
    global image, image_copy

    # 读取图片
    image = cv2.imread(image_path)
    if image is None:
        print("错误：无法加载图片！请检查路径。")
        return

    image_copy = image.copy()

    # 绑定鼠标事件
    cv2.namedWindow("Image")
    cv2.setMouseCallback("Image", draw_rectangle)

    print("按 's' 保存 YOLO 标注和带有边界框的图片, 'c' 切换缺陷类型, 'q' 退出")

    while True:
        cv2.imshow("Image", image_copy)
        key = cv2.waitKey(1) & 0xFF

        if key == ord("s"):  # 按 's' 保存标注和带有边界框的图片
            save_yolo_annotation(image_path)
            save_annotated_image(image_path)
        elif key == ord("c"):  # 按 'c' 切换缺陷类型
            switch_defect()
        elif key == ord("q"):  # 按 'q' 退出
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    img_path = "123.png"  # 替换为你的图片路径
    main(img_path)