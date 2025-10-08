from datetime import datetime, timedelta
from collections import defaultdict


def parse_timestamps(timestamps):
    """
    解析时间戳字符串为 datetime 对象

    :param timestamps: 时间戳字符串列表
    :return: datetime 对象列表
    """
    return [datetime.strptime(ts, '%Y-%m-%d %H:%M:%S') for ts in timestamps]


def find_dense_intervals(timestamps, num_intervals=3, interval_size=1800):
    """
    找出时间分布最密集的区间

    :param timestamps: datetime 对象列表
    :param num_intervals: 需要找出的最密集区间数量
    :param interval_size: 区间大小（以秒为单位）
    :return: 最密集的区间列表
    """
    if not timestamps:
        return []

    # 按时间排序
    timestamps.sort()

    # 初始化区间计数器
    interval_counts = defaultdict(int)

    # 计算每个区间的计数，按 interval_size 划分
    for ts in timestamps:
        # 计算当前时间戳所属的区间起始时间
        interval_start = ts - timedelta(seconds=ts.second, microseconds=ts.microsecond)
        interval_start -= timedelta(minutes=ts.minute % (interval_size // 60))
        interval_counts[interval_start] += 1

    # 找出最密集的区间
    sorted_intervals = sorted(interval_counts.items(), key=lambda x: x[1], reverse=True)
    dense_intervals = sorted_intervals[:num_intervals]

    return [(interval[0], interval[0] + timedelta(seconds=interval_size), interval[1]) for interval in dense_intervals]


# 用于对时间区间进行密度分析，其实就是看每一段时间里面有多少个数据点
# 从而判断是否在某个时间段里面，检测的缺陷数过多，从而为检测报告提供数据
def time_msg_extra(time_list: list, interval_size=1800, num_intervals=3):
    # 解析时间戳
    parsed_timestamps = parse_timestamps(time_list)

    # 找出最密集的几个区间，可以通过参数指定每个区间的长度和 最密集区间的个数
    # 比如 interval_size=1800 就是将时间划分为每30min
    dense_intervals = find_dense_intervals(parsed_timestamps, num_intervals=num_intervals, \
                                           interval_size=interval_size)
    time_msg = {}
    for idx, (start, end, count) in enumerate(dense_intervals):
        if idx == num_intervals:
            break
        key = f"时间区间: {start} - {end}"
        value = f"数据点数量: {count}"
        time_msg[key] = value

    return time_msg


# 示例用法
if __name__ == "__main__":
    # 示例时间戳列表
    timestamps = [
        '2023-07-01 12:00:00',
        '2023-07-01 12:01:00',
        '2023-07-01 12:02:00',
        '2023-07-01 12:03:00',
        '2023-07-01 12:04:00',
        '2023-07-01 12:05:00',
        '2023-07-01 12:10:00',
        '2023-07-01 12:11:00',
        '2023-07-01 12:12:00',
        '2023-07-01 12:13:00',
        '2023-07-01 12:14:00',
        '2023-07-01 12:15:00',
        '2023-07-01 12:20:00',
        '2023-07-01 12:21:00',
        '2023-07-01 12:22:00',
        '2023-07-01 12:23:00',
        '2023-07-01 12:24:00',
        '2023-07-01 12:25:00',
        '2023-07-01 12:30:00',
        '2023-07-01 12:31:00',
        '2023-07-01 12:32:00',
        '2023-07-01 12:33:00',
        '2023-07-01 12:34:00',
        '2023-07-01 12:35:00',
        '2023-07-01 13:40:00'
    ]

    parsed_timestamps = parse_timestamps(timestamps)

    dense_intervals = find_dense_intervals(parsed_timestamps, num_intervals=3, interval_size=1800)
    # print(dense_intervals)
    # 打印结果
    for start, end, count in dense_intervals:
        print(f"时间区间: {start} - {end}, 出现缺陷的数量: {count}")