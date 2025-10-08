import os
# from engine_infer import *
import shutil
import json
from collections import defaultdict
import numpy as np
from scipy.stats import zscore
from sklearn.cluster import DBSCAN


def remove_outliers_dbscan(points, eps=0.1, min_samples=1):
    """
    使用 DBSCAN 方法移除异常值

    :param points: 数据点列表，每个数据点是一个元组 (x, y)
    :param eps: DBSCAN 的邻域半径
    :param min_samples: DBSCAN 的最小样本数
    :return: 移除异常值后的数据点列表
    """
    if not points:
        return points
    
    points_array = np.array(points)
    dbscan = DBSCAN(eps=eps, min_samples=min_samples).fit(points_array)
    labels = dbscan.labels_
    
    # 标签为 -1 的点是噪声点（异常值）
    inliers = points_array[labels != -1]

    if inliers.shape[0] == 0:
        return points, (0,0)
    
    std_dev_x = np.std(points_array[:, 0])
    std_dev_y = np.std(points_array[:, 1])
    return inliers.tolist(), (round(std_dev_x, 6), round(std_dev_y, 6))

def remove_outliers_iqr(data, threshold=1.5):
    """
    使用 IQR 方法移除异常值

    :param data: 数据列表
    :param threshold: IQR 阈值
    :return: 移除异常值后的数据列表
    """
    q1 = np.percentile(data, 25)
    q3 = np.percentile(data, 75)
    iqr = q3 - q1
    lower_bound = q1 - threshold * iqr
    upper_bound = q3 + threshold * iqr
    return [data[i] for i in range(len(data)) if lower_bound <= data[i] <= upper_bound]

def extract_defect_info(defect_data):
    """
    提取缺陷类别、每种缺陷的分布区域和缺陷区域的平均长宽

    :param defect_data: 包含缺陷信息的列表
    :return: 缺陷类别列表, 每种缺陷的分布区域, 每种缺陷的平均长宽
    """
    defect_types = set()
    defect_type_cnt = {}
    defect_distribution = defaultdict(list)
    defect_avg_dimensions = defaultdict(list)
    defect_area_proportion = defaultdict(list)

    for defect in defect_data:
        defect_type = defect['defect_type']
        defect_types.add(defect_type)

        if defect_type not in defect_type_cnt:
            defect_type_cnt[defect_type] = 1
        else:
            defect_type_cnt[defect_type] += 1
        
        # 添加中心点到分布区域
        defect_distribution[defect_type].append((round(defect['x_center'], 6), round(defect['y_center'], 6)))
        
        # 添加宽度和高度到平均长宽
        defect_avg_dimensions[defect_type].append((round(defect['width'], 6), round(defect['height'], 6)))

        # 添加缺陷区域的面积
        defect_area_proportion[defect_type].append(round(defect['area_proportion'], 6))

    # 计算每种缺陷的平均中心点
    defect_distribution_avg = {}
    defect_center_std = {}
    for defect_type, points in defect_distribution.items():
        # 使用 DBSCAN 方法移除异常值
        points_cleaned, std_dev = remove_outliers_dbscan(points)
        
        # 提取 x 和 y 坐标
        x_coords = [point[0] for point in points_cleaned]
        y_coords = [point[1] for point in points_cleaned]
        
        # 计算平均值
        avg_x = sum(x_coords) / len(x_coords) if x_coords else 0
        avg_y = sum(y_coords) / len(y_coords) if y_coords else 0
        defect_distribution_avg[defect_type] = (round(avg_x, 6), round(avg_y, 6))

        # 存储标准差
        defect_center_std[defect_type] = std_dev, 6

    # 计算每种缺陷的平均宽度和高度
    defect_avg_dimensions_avg = {}
    for defect_type, dimensions in defect_avg_dimensions.items():
        # 提取宽度和高度
        widths = [dim[0] for dim in dimensions]
        heights = [dim[1] for dim in dimensions]
        
        # 使用 IQR 方法移除异常值
        widths_cleaned = remove_outliers_iqr(widths)
        heights_cleaned = remove_outliers_iqr(heights)
        
        # 计算平均值
        avg_width = sum(widths_cleaned) / len(widths_cleaned) if widths_cleaned else 0
        avg_height = sum(heights_cleaned) / len(heights_cleaned) if heights_cleaned else 0
        defect_avg_dimensions_avg[defect_type] = (round(avg_width, 6), round(avg_height, 6))
    
    # 计算每种缺陷的面积和面积方差
    defect_avg_area_proportion = {}
    defect_area_proportion_std = {}
    for defect_type, area in defect_area_proportion.items() :
        # 使用 IQR 方法移除异常值
        area_cleaned = remove_outliers_iqr(area)

        avg_area = sum(area_cleaned) / len(area_cleaned) if area_cleaned else 0
        std_area = np.std(area_cleaned) if area_cleaned else 0

        defect_avg_area_proportion[defect_type] = round(avg_area, 6)
        defect_area_proportion_std[defect_type] = round(std_area, 6)

    return list(defect_types), defect_type_cnt, defect_distribution_avg, defect_avg_dimensions_avg, \
        defect_center_std, defect_avg_area_proportion, defect_area_proportion_std

def extra_from_txts(file_paths):
    """
    读取所有txt文件的每一行数据并解析为JSON格式
    然后调用上面的函数进行数据提取处理
    
    :param file_path: 文件路径
    :return: 缺陷类别列表, 每种缺陷的分布区域, 每种缺陷的平均长宽
    """
    try:
        lines = []
        for path in file_paths :
            with open(path, 'r', encoding='utf-8') as file:
                lines.extend(file.readlines())
        
        # 去除每行末尾的换行符，并过滤空行
        lines = [line.strip() for line in lines if line.strip()]
        
        defect_data = []
        for line in lines:
            try:
                # 将每一行转换为字典
                items = line.split(', ')
                defect_dict = {}
                for item in items:
                    key, value = item.split(': ')
                    # 尝试将值转换为浮点数或整数
                    try:
                        value = float(value)
                    except ValueError:
                        pass
                    defect_dict[key] = value
                defect_data.append(defect_dict)
                # print(defect_dict)
            except Exception as e:
                print(f"解析行失败: {line}，错误信息: {e}")
        
        defect_types, defect_type_cnt, defect_distribution_avg, defect_avg_dimensions_avg, defect_center_std,\
        defect_avg_area_proportion, defect_area_proportion_std = extract_defect_info(defect_data)

        return defect_types, defect_type_cnt, defect_distribution_avg, defect_avg_dimensions_avg, defect_center_std,\
            defect_avg_area_proportion, defect_area_proportion_std
    
    except FileNotFoundError:
        print(f"文件 {file_path} 未找到")
        return None, None, None, None, None, None  
    except Exception as e:
        print(f"读取文件时发生错误: {e}")
        return None, None, None, None, None, None

# 示例用法
if __name__ == "__main__":
    # file_path = './test_out/inclusion_1.txt'
    file_path = ['./03db6bbc3.txt']

    defect_types, defect_type_cnt, defect_distribution_avg, defect_avg_dimensions_avg, defect_center_std,\
    defect_avg_area_proportion, defect_area_proportion_std = extra_from_txts(file_path)
    
    if defect_types is not None:
        print(f"缺陷类别: {defect_types}")
        print(f'每种缺陷出现的次数: {defect_type_cnt}')
        print(f"每种缺陷的分布区域 (平均中心点): {defect_distribution_avg}")
        print(f"每种缺陷的平均长宽: {defect_avg_dimensions_avg}")
        print(f"每种缺陷中心点的标准差: {defect_center_std}")
        print(f"每种缺陷的分布区域 (平均面积比例): {defect_avg_area_proportion}")
        print(f"每种缺陷的分布区域 (面积比例标准差): {defect_area_proportion_std}")
    else:
        print("读取文件失败")