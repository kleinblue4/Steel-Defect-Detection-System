from ultralytics import YOLO
from multiprocessing import freeze_support
import argparse


def eval_parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="YOLO 评估脚本")
    parser.add_argument('--model', type=str, default='./weights/best.pt', help='用于评估的模型的路径')
    parser.add_argument('--task', type=str, default='detect', help='模型的任务类型')
    parser.add_argument('--conf', type=float, default=0.1, help='模型推理时所设置的置信度阈值')
    parser.add_argument('--iou', type=float, default=0.6, help='模型推理中，非极大值抑制的iou阈值')
    parser.add_argument('--yaml', type=str, default='./yaml/neu-det.yaml', help='评估模型时所使用的数据集及其信息')
    parser.add_argument('--name', type=str, default='eval', help='存放评估结果的文件夹名称')
    return parser.parse_args()


def eval_main(args):
    # 加载模型
    model = YOLO(args.model, task=args.task)
    # print(3)

    # # 验证模型，并设置当前的置信度阈值
    metrics = model.val(data=args.yaml, conf=args.conf, name=args.name, iou=args.iou)

    # # 打印 mAP50
    print(f"mAP50: {metrics.box.map50}")
    return metrics.box.map50
