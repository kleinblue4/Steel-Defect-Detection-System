from ultralytics import YOLO
from multiprocessing import freeze_support
import argparse
import os


def train_parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="YOLO 训练脚本")
    parser.add_argument('--model', type=str, default='yolov8n.pt', help='模型文件路径 (例如: yolov8n.pt, yolov11.pt)')
    parser.add_argument('--data', type=str, default='./yaml/neu-det.yaml', help='数据集配置文件路径')
    parser.add_argument('--epochs', type=int, default=300, help='训练的总轮数')
    parser.add_argument('--imgsz', type=int, default=300, help='输入图像的尺寸')
    parser.add_argument('--batch', type=int, default=16, help='批量大小')
    parser.add_argument('--name', type=str, default=None, help='训练任务的名称（默认为模型名称 + 数据集名称）')
    parser.add_argument('--val', type=bool, default=True, help='是否启用验证')
    parser.add_argument('--plots', type=bool, default=True, help='是否生成训练图表')
    parser.add_argument('--workers', type=int, default=0, help='数据加载的工作线程数')
    return parser.parse_args()


def train_main(args):
    """主训练函数"""
    # 如果未指定任务名称，则自动生成
    if args.name is None:
        model_name = os.path.splitext(os.path.basename(args.model))[0]  # 提取模型名称（去掉 .pt）
        data_name = os.path.splitext(os.path.basename(args.data))[0]  # 提取数据集名称（去掉 .yaml）
        args.name = f"{model_name}_{data_name}"  # 组合模型名称和数据集名称

    # 加载模型
    model = YOLO(args.model)

    # 训练模型
    results = model.train(
        data=args.data,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        name=args.name,
        val=args.val,
        plots=args.plots,
        workers=args.workers
    )
