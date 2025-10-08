import os
from engine_infer import *
import shutil
def delete_file_or_directory(path):
    """
    删除指定的文件或文件夹及其内容

    :param path: 文件或文件夹的路径
    """
    try:
        if os.path.isfile(path):
            os.remove(path)
            print(f"文件 {path} 已删除")
        elif os.path.isdir(path):
            shutil.rmtree(path)
            print(f"文件夹 {path} 及其内容已删除")
        else:
            print(f"路径 {path} 不存在")
    except Exception as e:
        print(f"删除路径 {path} 时发生错误: {e}")


def read_from_file(file_path):
    """
    读取txt文件的每一行数据

    :param file_path: 文件路径

    :return: 缺陷类别信息: defect_info 
    :return: 每个缺陷的面积占比: defect_proportion
    """
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
        # 去除每行末尾的换行符
        lines = [line.strip() for line in lines]
        defect_info = None
        defect_proportion = ""

        for idx, line in enumerate(lines) :
            if idx == 0 :
                defect_info = line
            else :
                defect_proportion += line 
        return defect_info, defect_proportion
    
    except FileNotFoundError:
        print(f"文件 {file_path} 未找到")
        return None, None  
    except Exception as e:
        print(f"读取文件时发生错误: {e}")
        return None, None

# 示例用法
if __name__ == "__main__":
    # path = './tt'
    # delete_file_or_directory(path)

    file_path = './test_out/03db6bbc3.txt'
    defect_info, defect_proportion = read_from_file(file_path)
    if defect_info is not None:
        print(f"缺陷类别信息: {defect_info}")
        print(f"每个缺陷的面积占比: {defect_proportion}")
    else:
        print("读取文件失败")

