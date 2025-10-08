from ultralytics import YOLO
import os
import numpy as np
import argparse
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import shutil
from DataBase_Modules.DataBase import DataBase
import cv2


def infer_parse_args():
    parser = argparse.ArgumentParser(description="YOLOv11 for Infer")
    parser.add_argument('--model', type=str, default='./best.pt',
                        help='模型的文件路径，支持pt、engine模型格式')
    parser.add_argument('--task', type=str, default='detect', help='任务类型，默认为：detect')
    parser.add_argument('--img_path', type=str, default=None, help='推理图片的路径，也支持多张图片推理')
    parser.add_argument('--img_dir', type=str, default='./input', help='批量推理图片的文件夹路径')
    parser.add_argument('--save_path', type=str, default='./infer_result', help='推理图片保存的文件夹路径')
    parser.add_argument('--report_generate', type=bool, default=False, help='是否基于检测结果生成报告')
    parser.add_argument('--multi_thread', type=int, default=1, help='模型推理的线程数，默认为1')
    parser.add_argument('--batch', type=int, default=1, help='模型推理的batch数，默认为1')
    parser.add_argument('--conf', type=float, default=0.25, help='模型推理中缺陷区域的置信度阈值')
    parser.add_argument('--iou', type=float, default=0.75, help='模型推理中，非极大值抑制的iou阈值')
    parser.add_argument('--conf_thread', type=float, default=0.4,
                        help='推理结果的置信度阈值，若结果的置信度低于阈值，则将该图片视为难例并保存')
    parser.add_argument('--hard_dir', type=str, default='./hard_example', help='难例图片的保存路径')
    return parser.parse_args()


# 新的 HSV 调整函数（伽马校正）
def adjust_hsv(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    v = hsv[..., 2].astype(float) / 255.0  # 归一化到[0,1]

    gamma = 0.8  # 调整参数：0.5~0.8 通常效果较好
    v_corrected = np.power(v, gamma)

    v_corrected = np.clip(v_corrected * 255, 0, 255).astype(np.uint8)
    hsv[..., 2] = v_corrected

    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)


# 计算V通道的平均亮度值
def calculate_v_mean(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    v_mean = np.mean(hsv[..., 2])
    return v_mean


# 对图片数据做增强处理，调节亮度
def image_augment(image):
    v_mean = calculate_v_mean(image)
    thread = 128
    if v_mean < thread:
        adjusted_image = adjust_hsv(image)
        return adjusted_image
    else:
        return image


def thread_infer(img_paths, model_path, task, args):
    '''
    多线程推理
    :param img_paths: 图片路径列表
    :param model_path: 模型路径
    :param task: 任务类型
    :param args: 命令行参数
    '''
    model = YOLO(model_path, task=task, verbose=False)
    result_paths = []
    for i in range(0, len(img_paths), args.batch):
        batch_images_paths = img_paths[i:i + args.batch]
        # batch_images = [image_augment(cv2.imread(img_path)) for img_path in batch_images_paths]
        batch_images = [cv2.imread(img_path) for img_path in batch_images_paths]

        results = model.predict(batch_images)

        for img_path, result in zip(batch_images_paths, results):
            img_path = img_path.replace('\\','/')
            output = result.plot()
            output_path = os.path.join(args.save_path, img_path.split('/')[-1])
            cv2.imwrite(output_path, output)
            result_paths.append(output_path)  # 添加结果路径到列表

            # defect_position = []
            # for box in result.boxes:
            #     class_id = int(box.cls)
            #     height, width = box.orig_shape
            #     class_name = result.names[class_id]
            #     bbox = box.xywh[0].cpu().numpy()  # 获取边界框的 (x_center, y_center, width, height)
            #     area = 1.0 * bbox[2] * bbox[3] / (height * width) # 计算面积 (width * height)
            #     defect_position.append({
            #         'defect_type': class_name,
            #         'x_center': bbox[0] / width,
            #         'y_center': bbox[1] / height,
            #         'width': bbox[2] / width,
            #         'height': bbox[3] / height,
            #         'area_proportion': area
            #     })

            # txt_path = img_path.split('/')[-1].split('.')[0] + '.txt'
            # with open(os.path.join(args.save_path, txt_path), mode='w') as f :
            #     #  写入 defect_position 信息
            # for defect in defect_position:
            #     f.write(f"defect_type: {defect['defect_type']}, "
            #             f"x_center: {defect['x_center']}, "
            #             f"y_center: {defect['y_center']}, "
            #             f"width: {defect['width']}, "
            #             f"height: {defect['height']}, "
            #             f"area_proportion: {defect['area_proportion']:.4f}\n")

            # ------------------- 以这边的写的为准，之前推理结果之保存了面积的占比 -----------------------------
            defect_area_proportion = {}
            defect_position = []
            for box in result.boxes:
                class_id = int(box.cls)
                height, width = box.orig_shape
                class_name = result.names[class_id]
                bbox = box.xywh[0].cpu().numpy()  # 获取边界框的 (x_center, y_center, width, height)
                area = 1.0 * bbox[2] * bbox[3] / (height * width)  # 计算面积 (width * height)
                if class_name not in defect_area_proportion:
                    defect_area_proportion[class_name] = 0
                # defect_area_proportion[class_name] += area
                defect_position.append({
                    'defect_type': class_name,
                    'x_center': bbox[0] / width,
                    'y_center': bbox[1] / height,
                    'width': bbox[2] / width,
                    'height': bbox[3] / height,
                    'area_proportion': area
                })

            defect_type = defect_area_proportion.keys()

            with open(os.path.join(args.save_path, img_path.split('/')[-1].split('.')[0].split('\\')[-1] + '.txt'), mode='w') as f:
                f.write(" ".join(defect_type) + "\n")  # 将 dict_keys 转换为字符串并写入文件
                for defect in defect_position:
                    f.write(f"defect_type: {defect['defect_type']}, "
                            f"x_center: {defect['x_center']}, "
                            f"y_center: {defect['y_center']}, "
                            f"width: {defect['width']}, "
                            f"height: {defect['height']}, "
                            f"area_proportion: {defect['area_proportion']:.4f}\n")

            # for defect_type, area_proportion in defect_area_proportion.items():
            #     f.write(f"{defect_type}:{area_proportion:.4f} ")
        # -------------------------------------------------------------------------------------------------------------------
    return result_paths


def infer_images(img_paths, args):
    """
    进行图片推理的函数
    :param img_paths: 图片路径列表
    :param args: 命令行参数
    :return: None
    """
    if args.save_path and not os.path.exists(args.save_path):
        os.makedirs(args.save_path, exist_ok=True)
    if args.hard_dir and not os.path.exists(args.hard_dir):
        os.makedirs(args.hard_dir, exist_ok=True)

    start_time = time.time()

    # 将图片路径列表分成多个子列表
    num_threads = args.multi_thread
    img_paths_split = [img_paths[i::num_threads] for i in range(num_threads)]

    # 添加调试信息，确保所有图片路径都被分配
    # all_allocated_paths = []
    # for sublist in img_paths_split:
    #     all_allocated_paths.extend(sublist)
    # assert set(all_allocated_paths) == set(img_paths), "Not all image paths are allocated to sublists"

    all_result_paths = []
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = []
        for img_paths_sublist in img_paths_split:
            # 提交每个子列表到线程池，并传递模型路径和任务类型
            futures.append(executor.submit(thread_infer, img_paths_sublist, args.model, args.task, args))

        for future in as_completed(futures):
            result_paths = future.result()  # 获取每个线程的结果路径列表
            all_result_paths.extend(result_paths)  # 合并结果路径列表

    end_time = time.time()
    time_cost = end_time - start_time

    print(f'infer ok!\n total time cost: {time_cost}\n \
          total_image_num: {len(img_paths)}, FPS: {len(img_paths) / time_cost}')
    return all_result_paths


# 纯推理下，FPS：80-90,
# 若进行图像增强和结果保存，FPS：70
def infer_main(args):
    if args.img_path is not None:
        img_path_list = [i for i in args.img_path.split(',')]
    elif args.img_dir is not None:
        img_path_list = [os.path.join(args.img_dir, i)
                         for i in os.listdir(args.img_dir)]
    else:
        print('请输入图片路径或文件夹路径')
        return

    # 如果没有指定保存路径，则默认保存在当前目录下的temp文件夹
    if args.save_path is None:
        args.save_path = './temp'
        os.makedirs(args.save_path, exist_ok=True)

    # 返回得到所有的推理结果图片路径（推理结果图 和 缺陷详细信息同名）
    # 在后续选择将推理结果插入到数据库里面的时候，可以读取这些推理结果图片和信息
    result_paths = infer_images(img_path_list, args)

    return result_paths


# if __name__ == '__main__':
#     args = parse_args()
#
#     main(args)

''' 关于如何在别的函数里面调用这个推理函数 -- 示例  '''
#     from engine_infer import *
# if __name__ == "__main__":
#     args = parse_args()
#     args.model = './weights/best.pt'
#     args.task = 'detect'
#     args.save_path = './test_out'
#     args.img_dir = './test_input'
#     args.multi_thread = 4
#     args.batch = 2
#     main(args)