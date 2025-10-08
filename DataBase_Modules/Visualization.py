from matplotlib import pyplot as plt
import numpy as np
import seaborn as sns
import pandas as pd
from matplotlib.dates import DateFormatter, AutoDateLocator
from matplotlib.font_manager import FontProperties
import matplotlib

font_path = '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'  # 替换为实际的字体路径
font_prop = FontProperties(fname=font_path)

# 设置中文字体
matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # 选择一个支持中文的字体
matplotlib.rcParams['axes.unicode_minus'] = False  # 解决保存图像是负号'-'显示为方块的问题

# font_path = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc' # 替换为实际路径
# font = FontProperties(fname=font_path)

def plot_defect_type_pie_chart(defect_type_cnt, save_path=None):
    if not isinstance(defect_type_cnt, dict):
        print("Error: defect_type_cnt should be a dictionary.")
        return

    if not defect_type_cnt:
        print("Error: defect_type_cnt is empty.")
        return

    labels = list(defect_type_cnt.keys())
    sizes = list(defect_type_cnt.values())

    plt.figure(figsize=(8, 8))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.title('缺陷类型频率分布', fontproperties=font_prop)

    if save_path:
        plt.savefig(save_path)

    plt.show()


def plot_defect_center_distribution(defect_data, save_path=None):
    # 将字典转换为DataFrame
    data = []
    for defect_type, points in defect_data.items():
        for x, y in points:
            data.append({'defect_type': defect_type, 'x_center': x, 'y_center': y})

    df = pd.DataFrame(data)

    # 定义不同的标记
    markers = {'class3': 'o', 'class4': 's', 'scratch': '^', 'other': 'D'}  # 根据需要添加更多标记

    plt.figure(figsize=(10, 6))
    for defect_type, group in df.groupby('defect_type'):
        plt.scatter(group['x_center'], group['y_center'], label=defect_type, marker=markers.get(defect_type, 'o'))

    plt.title('缺陷中心点分布', fontproperties=font_prop)
    plt.xlabel('X 中心', fontproperties=font_prop)
    plt.ylabel('Y 中心', fontproperties=font_prop)
    plt.legend(title='缺陷类型', title_fontproperties=font_prop)

    if save_path:
        plt.savefig(save_path)

    plt.show()


def plot_defect_area_proportion_distribution(defect_data, save_path=None):
    # 将字典转换为DataFrame
    x_data = []
    y_data = []
    for defect_type, proportions in defect_data.items():
        x_data.append(defect_type)
        y_data.append(sum(proportions) / len(proportions))

    x_data = np.array(x_data)
    y_data = np.array(y_data)

    plt.figure(figsize=(10, 6))
    plt.bar(x_data, y_data)
    plt.title('缺陷面积占比分布', fontproperties=font_prop)
    plt.xlabel('缺陷类型', fontproperties=font_prop)
    plt.ylabel('面积占比', fontproperties=font_prop)

    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()  # 自动调整子图参数，防止标签被截断

    if save_path:
        plt.savefig(save_path)

    plt.show()


def plot_defect_time_distribution(time_msg, save_path=None):
    # 解析 time_msg 字典
    intervals = []
    counts = []
    for key, value in time_msg.items():
        interval = key.split(': ')[1]  # 提取时间区间
        count = int(value.split(': ')[1])  # 提取数据点数量
        intervals.append(pd.to_datetime(interval.split(' - ')[0]))  # 取时间区间的开始时间
        counts.append(count)

    # 创建 DataFrame
    df = pd.DataFrame({'interval': intervals, 'count': counts})

    plt.figure(figsize=(15, 6))  # 增加图表宽度
    plt.plot(df['interval'], df['count'], marker='o')
    plt.title('缺陷检测时间分布', fontproperties=font_prop)
    plt.xlabel('时间区间', fontproperties=font_prop)
    plt.ylabel('缺陷数量', fontproperties=font_prop)

    # 使用 AutoDateLocator 和 DateFormatter 自动调整日期标签
    ax = plt.gca()
    ax.xaxis.set_major_locator(AutoDateLocator())
    ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d %H:%M:%S'))

    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()  # 自动调整子图参数，防止标签被截断

    if save_path:
        plt.savefig(save_path)

    plt.show()


if __name__ == '__main__':
    print()
    plot_defect_time_distribution({'2023-10-01': 10, '2023-10-02': 15})