import mysql.connector
import os
from datetime import datetime
import subprocess
from DataBase_Modules.defect_utils import *
from DataBase_Modules.time_utiles import *
from DataBase_Modules.Visualization import *


# 这里将创建数据库的函数单独放出来，是为了在用户第一次创建数据库的时候提供调用方法
def Create_Database(sql_file_path: str, host: str, user: str, password: str, database_name: str):
    try:
        if not os.path.exists(sql_file_path):
            print(f"文件不存在: {sql_file_path}")
            return

        # 读取 SQL 文件内容
        with open(sql_file_path, 'r', encoding='utf-8') as file:
            sql_content = file.read()

        # 自定义创建的数据库名称
        sql_content = sql_content.format(database_name=database_name)

        # 构建命令
        command = [
            '/usr/bin/mysql',
            "-h", host,
            "-u", user,
            "-p" + password,  # 确保密码正确拼接
        ]

        # 执行命令并从 SQL 文件中创建数据库
        result = subprocess.run(command, input=sql_content, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode != 0:
            print(f"创建数据库失败，错误信息:\n{result.stderr}")
        else:
            print(f"数据库创建成功，SQL 文件: {sql_file_path}")
    except subprocess.CalledProcessError as e:
        print(f"执行命令失败，错误信息:\n{e.output}")
    except Exception as e:
        print(f"发生错误: {e}")


class DataBase():
    def __init__(self, host, user, password, database, mysql_path=None, mysqldump_path=None):
        # 连接数据库的配置
        self.DB_CONFIG = {
            'host': host,  # 数据库的主机
            'user': user,  # 用户名：root
            'password': password,  # 密码
            'database': database,  # 数据库名
        }
        # 这里需要提前安装Mysql，然后指定mysql和mysqldump的安装路径
        self.mysql_path = mysql_path
        self.mysqldump_path = mysqldump_path
        self.Detection_results_parm = ['image_name', 'image_type', 'image_data',
                                       'defect_result']
        self.Defect_details_parm = ['result_image_name', 'detection_result_id', 'defect_type',
                                    'x_center', 'y_center', 'width', 'height', 'area_proportion']
        self.Annotation_data_parm = ['image_name', 'image_type', 'image_data',
                                     'yolo_anno', 'annotation_image']
        self.Detection_reports_parm = ['report_file_name', 'report_file_type', 'report_file', 'report_time']

        try:
            self.conn = mysql.connector.connect(**self.DB_CONFIG)
            self.cursor = self.conn.cursor()
            print("数据库连接成功！")
        except mysql.connector.Error as e:
            print(f"无法连接到MySQL数据库，报错: {e}")
            self.conn = None
            self.cursor = None

    # 重新连接数据库
    def Reconnect_Database(self):
        try:
            self.conn = mysql.connector.connect(**self.DB_CONFIG)
            self.cursor = self.conn.cursor()
            return True, 1
        except mysql.connector.Error as e:
            print(f"无法连接到MySQL数据库，报错: {e}")
            self.conn = None
            self.cursor = None
            return False, e

    # 释放数据库资源
    def Release_Database(self):
        if self.cursor is not None:
            self.cursor.close()
        if self.conn is not None:
            self.conn.close()

    # 读取二进制的图片数据或文件
    def read_binary_data(self, image_path: str):
        if not os.path.exists(image_path):
            print(f"文件不存在: {image_path}")
            return None
        with open(image_path, "rb") as file:
            image_data = file.read()
            return image_data

    # 读取检测结果的txt文件，其中包含每个缺陷的类别、位置、面积等信息
    def read_txt_file(self, txt_path: str):
        try:
            if not os.path.exists(txt_path):
                print(f"文件不存在: {txt_path}")
                return None
            with open(txt_path, "r", encoding='utf-8') as file:
                lines = file.readlines()

            # 去除每行末尾的换行符，并过滤空行
            lines = [line.strip() for line in lines if line.strip()]

            defect_data = []

            cnt = 1  # cnt 用来跳过txt'的第一行 ----------------------------------------------------------------------------------------

            for line in lines:
                if cnt == 1:  # 因为推理结果txt的第一行是缺陷类型，所以跳过不读取 -------------------------------------------------------
                    cnt = cnt + 1
                    continue
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
                except Exception as e:
                    print(f"解析行失败: {line}，错误信息: {e}")
            return defect_data

        except Exception as e:
            print(f"读取文件{txt_path}时发生错误: {e}")

    # 插入缺陷检测的结果图片和数据
    # 包括：检测结果图片、图片名称、图片类型、缺陷掩码、缺陷类型
    def Insert_Detected_Image_Data(self, image_path: str, defect_result_path: str):
        try:
            image_name = image_path.split("/")[-1].split('\\')[-1]
            image_type = image_name.split(".")[-1]

            # 读取二进制的图片数据
            image_data = self.read_binary_data(image_path)
            if image_data is None:
                print(f"读取图片{image_name}数据失败！")
                return

            defect_mask_name = defect_result_path.split("/")[-1]
            defect_result = self.read_binary_data(defect_result_path)
            if defect_result is None:
                print(f"读取{defect_mask_name}数据失败！")
                return

            sql = """
            INSERT INTO Detection_results (
                image_name, image_type, image_data, defect_result, upload_time
            ) VALUES (
                %s, %s, %s, %s, %s
            ) ON DUPLICATE KEY UPDATE
                image_type = VALUES(image_type),
                image_data = VALUES(image_data),
                defect_result = VALUES(defect_result),
                upload_time = VALUES(upload_time)
            """
            self.cursor.execute(sql, (image_name, image_type, image_data, defect_result, datetime.now().strftime("%Y-%m-%d_%H:%M:%S")))
            # print(image_name)
            # print(image_type)
            self.conn.commit()
            # print(f"图片数据{image_name}插入成功！")

        except mysql.connector.Error as e:
            print(f"数据库错误: {e}")
        except Exception as e:
            print(f"操作数据时发生错误: {e}")

    # 插入缺陷检测的结果详情，这边只读取txt信息然后插入到数据库中，如果需要可以修改
    def Insert_Detected_Details(self, detection_result_id: int,
                                result_image_name: str, txt_path: str):
        try:
            defect_infos = self.read_txt_file(txt_path)
            sql = """
            INSERT INTO Defect_details (
                result_image_name, detection_result_id, defect_type,
                x_center, y_center, width, height, area_proportion, upload_time
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s
            ) ON DUPLICATE KEY UPDATE
                result_image_name = VALUES(result_image_name),
                detection_result_id = VALUES(detection_result_id),
                defect_type = VALUES(defect_type),
                x_center = VALUES(x_center),
                y_center = VALUES(y_center),
                width = VALUES(width),
                height = VALUES(height),
                area_proportion = VALUES(area_proportion),
                upload_time = VALUES(upload_time)
            """
            # print(defect_infos)
            for info in defect_infos:
                params = (result_image_name, detection_result_id, info['defect_type'],
                                          info['x_center'], info['y_center'], info['width'], info['height'],
                                          info['area_proportion'],
                                          datetime.now().strftime("%Y-%m-%d_%H:%M:%S"))
                self.cursor.execute(sql, params)
                self.conn.commit()

            # print('缺陷详细信息插入成功！')

        except mysql.connector.Error as e:
            print(f"数据库错误: {e}")
        except Exception as e:
            print(f"操作数据时发生错误: {e}")

    # 插入标注缺陷区域的数据，后期用作训练模型的数据
    # 包括：图片名称、图片类型、图片数据、缺陷掩码、缺陷信息
    def Insert_Annotation_Data(self, image_path: str, anno_image_path: str,
                               yolo_anno_path: str):
        try:
            image_name = image_path.split('/')[-1]
            image_type = image_name.split(".")[-1]
            image_data = self.read_binary_data(image_path)
            if image_data is None:
                print(f"读取{image_name}数据失败！")
                return

            anno_image_name = anno_image_path.split('/')[-1]
            anno_image = self.read_binary_data(anno_image_path)
            if anno_image is None:
                print(f"读取{anno_image_name}数据失败！")
                return

            yolo_anno_name = yolo_anno_path.split('/')[-1]
            yolo_anno = self.read_binary_data(yolo_anno_path)
            if yolo_anno is None:
                print(f"读取{yolo_anno_name}数据失败！")
                return

            sql = """
            INSERT INTO Annotation_data (
                image_name, image_type, image_data, annotation_image, yolo_anno, upload_time
            ) VALUES (
                %s, %s, %s, %s, %s, %s
            ) ON DUPLICATE KEY UPDATE
                image_name = VALUES(image_name),
                image_type = VALUES(image_type),
                image_data = VALUES(image_data),
                annotation_image = VALUES(annotation_image),
                yolo_anno = VALUES(yolo_anno),
                upload_time = VALUES(upload_time)
            """
            self.cursor.execute(sql, (image_name, image_type, image_data, anno_image, \
                                      yolo_anno, datetime.now().strftime("%Y-%m-%d_%H:%M:%S")))
            self.conn.commit()
            # print(f'图片数据{image_name}插入成功！')

        except mysql.connector.Error as e:
            print(f"数据库错误: {e}")
        except Exception as e:
            print(f"操作数据时发生错误: {e}")

    # 插入缺陷检测的结果报告
    # 包括：报告文件名、报告文件类型、报告文件、报告上传的时间
    def Insert_Detection_Report(self, report_path: str):
        try:
            report_name = report_path.split("/")[-1]
            report_type = report_name.split(".")[-1]
            report_data = self.read_binary_data(report_path)
            if report_data is None:
                print(f"读取{report_name}数据失败！")
                return
            sql = """
            INSERT INTO Detection_reports (
                report_file_name, report_file_type, report_file, report_time
            ) VALUES (
                %s, %s, %s, %s
            ) ON DUPLICATE KEY UPDATE
                report_file_name = VALUES(report_file_name),
                report_file_type = VALUES(report_file_type),
                report_file = VALUES(report_file),
                report_time = VALUES(report_time)
            """
            self.cursor.execute(sql, (report_name, report_type, report_data, \
                                      datetime.now().strftime("%Y-%m-%d_%H:%M:%S")))
            self.conn.commit()
            # print(f"检测报告{report_name}插入成功！")

        except mysql.connector.Error as e:
            print(f"数据库错误: {e}")
        except Exception as e:
            print(f"操作数据时发生错误: {e}")

    # 查询缺陷检测的结果数据，支持一次查询多条数据，查询过程通过id来查询
    def Get_Detected_Image(self, image_ids: list, save_path: str):
        try:
            if not os.path.exists(save_path):
                os.makedirs(save_path, exist_ok=True)

            placeholders = ', '.join(['%s'] * len(image_ids))
            sql = f"""
            SELECT image_name, image_type, image_data, defect_result
            FROM Detection_results
            WHERE id IN ({placeholders})
            """
            self.cursor.execute(sql, image_ids)
            results = self.cursor.fetchall()

            if not results:
                print('未找到图片数据')
                return

            for result in results:
                # 查询的每一条结果
                image_name, image_type, image_data, defect_result = result
                image_file_path = f'{save_path}/{image_name}'
                with open(image_file_path, "wb") as file:
                    file.write(image_data)

                detect_result_file_path = f'{save_path}/{image_name.split(f".{image_type}")[0]}_result.png'
                with open(detect_result_file_path, "wb") as file:
                    file.write(defect_result)

        except mysql.connector.Error as e:
            print(f'数据库错误: {e}')
        except Exception as e:
            print(f'错误: {e}')

    # 获取详细的检测结果信息
    def Get_Defect_Details(self, defect_ids: list, save_path: str):
        try:
            if not os.path.exists(save_path):
                os.makedirs(save_path, exist_ok=True)

            placeholders = ', '.join(['%s'] * len(defect_ids))
            sql = f"""
            SELECT result_image_name, detection_result_id, defect_type, x_center,
            y_center, width, height, area_proportion, upload_time FROM Defect_details
            WHERE id IN ({placeholders})
            """
            self.cursor.execute(sql, defect_ids)
            results = self.cursor.fetchall()

            if not results:
                print('未查找到数据\n')
                return

            # 这边对于检测信息的详细结果不需要保存到本地，如果需要显示到QT，那可以直接改掉
            for result in results:
                result_image_name, detection_result_id, defect_type, x_center, \
                    y_center, width, height, area_proportion, upload_time = result

                # print(f'{result_image_name} - defect: {defect_type}')
                # print(
                    # f'defect center: {x_center}, {y_center} 。 width: {width}, height: {height}, area_proportion: {area_proportion}')

            return results
        except mysql.connector.Error as e:
            print(f'数据库错误: {e}')
        except Exception as e:
            print(f'错误: {e}')

    # 查询缺陷检测的报告文件，支持一次查询多条数据，查询过程通过id来查询
    def Get_Report_File(self, file_ids: list, save_path: str):
        try:
            if not os.path.exists(save_path):
                os.makedirs(save_path, exist_ok=True)
            placeholders = ', '.join(['%s'] * len(file_ids))
            sql = f"""
                SELECT report_file_name, report_file_type, report_file
                FROM Detection_reports
                WHERE id IN ({placeholders})
            """
            self.cursor.execute(sql, file_ids)
            results = self.cursor.fetchall()

            if not results:
                print("没有找到对应的报告文件。")
                return

            for result in results:
                file_name, file_type, file_data = result
                file_path = os.path.join(save_path, file_name)
                with open(file_path, 'wb') as file:
                    file.write(file_data)
                # print(f"报告文件 {file_name} 保存成功。")
        except mysql.connector.Error as e:
            print(f"数据库错误: {e}")
        except Exception as e:
            print(f"发生错误: {e}")

    # 查询标注的数据
    def Get_Annotation_Data(self, image_ids: list, save_path: str):
        try:
            if not os.path.exists(save_path):
                os.makedirs(save_path, exist_ok=True)
            placeholders = ",".join(["%s"] * len(image_ids))
            sql = f"""
            SELECT image_name, image_type, image_data, annotation_image, yolo_anno
            FROM Annotation_data
            WHERE id IN ({placeholders})
            """
            self.cursor.execute(sql, image_ids)
            results = self.cursor.fetchall()

            if not results:
                print("未找到指定 ID 的图片")
                return
            for result in results:
                image_name, image_type, image_data, annotation_image, yolo_anno = result
                image_path = f"{save_path}/{image_name}"
                with open(image_path, "wb") as file:
                    file.write(image_data)

                annotation_image_path = f'{save_path}/{image_name.split(".")[0]}_anno.{image_type}'
                with open(annotation_image_path, "wb") as file:
                    file.write(annotation_image)

                yolo_anno_path = f'{save_path}/{image_name.split(".")[0]}_anno.txt'
                with open(yolo_anno_path, 'wb') as file:
                    file.write(yolo_anno)

                print(
                    f'图片已保存为 {image_name}, 缺陷标注已保存为 {annotation_image_path}, yolo标注结果保存为 {yolo_anno_path}')

        except mysql.connector.Error as e:
            print(f"数据库错误: {e}")
        except Exception as e:
            print(f"发生错误: {e}")

    # 对数据库进行备份，备份的位置在：backup_file , eg: ./backup/data.sql
    def Backup_DataBase(self, backup_file: str):
        try:
            command = [
                self.mysqldump_path,  # mysqldump 的路径
                "-h", self.DB_CONFIG['host'],
                "-u", self.DB_CONFIG['user'],
                f"-p{self.DB_CONFIG['password']}",  # 修复密码参数格式
                self.DB_CONFIG['database']
            ]

            backup_dir = os.path.dirname(backup_file)

            # 如果备份目录不存在，则创建
            if backup_dir and not os.path.exists(backup_dir):
                os.makedirs(backup_dir, exist_ok=True)
                print(f"创建备份目录: {backup_dir}")

            # 执行 mysqldump 命令并保存输出到备份文件
            with open(backup_file + '.sql', 'w') as file:
                result = subprocess.run(command, stdout=file, stderr=subprocess.PIPE, text=True)

            # 检查命令是否成功执行
            if result.returncode != 0:
                print(f"备份数据失败，错误信息:\n{result.stderr}")
            else:
                print(f"备份数据完成，备份文件保存在: {backup_file + '.sql'}")
        except Exception as e:
            print(f"发生错误: {e}")

    # 恢复数据库的文件，将备份的数据库进行恢复，但是会覆盖掉当前数据库里面的数据
    # 所以在使用恢复数据库的方法之前，最好先备份数据库
    def Restore_Database(self, backup_file: str) -> None:
        try:
            # 检查备份文件是否存在
            if not os.path.exists(backup_file):
                print(f"备份文件不存在: {backup_file}")
                return

            # 构建 mysql 命令
            command = [
                # 注意，这边需要填写的是mysql的安装路径
                self.mysql_path,
                "-h", self.DB_CONFIG['host'],
                "-u", self.DB_CONFIG['user'],
                f"-p{self.DB_CONFIG['password']}",
                self.DB_CONFIG['database'],
                "--default-character-set=utf8"
            ]

            # 执行命令并从备份文件中恢复数据库
            with open(backup_file, 'r', encoding='utf-8') as file:
                result = subprocess.run(command, stdin=file, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            if result.returncode != 0:
                print(f"恢复失败，错误信息:\n{result.stderr}")
            else:
                print(f"数据库恢复成功，从备份文件: {backup_file}")


        except subprocess.CalledProcessError as e:
            print(f"恢复数据库时发生错误: {e}")
        except Exception as e:
            print(f"发生错误: {e}")

    # 删除检测结果图像，需要注意的是，删除了图片数据也会同步删除Defect_details表中的对应数据
    def Delete_Detected_Image_Data(self, image_ids: str):
        try:
            if len(image_ids) == 0:
                print("没有提供所要删除的图像ID")
                return

            placeholders = ",".join(["%s"] * len(image_ids))
            sql = f"""
            DELETE FROM Detection_results
            WHERE id IN ({placeholders})
            """
            self.cursor.execute(sql, image_ids)
            self.conn.commit()
            # print("删除成功！")

        except mysql.connector.Error as e:
            print(f"数据库错误: {e}")
        except Exception as e:
            print(f"发生错误: {e}")

    # 删除指定的缺陷详细数据。但是有一点需要注意，因为detection_result_id作为外键与Detection_results表中的id绑定，
    # 所以如果删除Detection_results中的图片数据，那么也会自动删除Defect_details表中的对应数据。
    # 所以这边的这个功能主要是指定某个缺陷数据进行删除
    def Delete_Defect_Details(self, defect_ids: str):
        try:
            if len(defect_ids) == 0:
                print("没有提供所要删除的缺陷ID")
                return

            placeholders = ",".join(["%s"] * len(defect_ids))
            sql = f"""
            DELETE FROM Defect_details
            WHERE id IN ({placeholders})
            """
            self.cursor.execute(sql, defect_ids)
            self.conn.commit()
            # print("删除成功！")
        except mysql.connector.Error as e:
            print(f"数据库错误: {e}")
        except Exception as e:
            print(f"发生错误: {e}")

    # 删除标注缺陷的图像数据
    def Delete_Annotation_Data(self, image_ids: str):
        try:
            if len(image_ids) == 0:
                print("没有提供所要删除的图像ID")
                return
            placeholders = ",".join(["%s"] * len(image_ids))
            sql = f"""
            DELETE FROM Annotation_data
            WHERE id IN ({placeholders})
            """
            self.cursor.execute(sql, image_ids)
            self.conn.commit()
            # print("删除成功！")

        except mysql.connector.Error as e:
            print(f'数据库报错: {e}')
        except Exception as e:
            print(f"发生错误: {e}")

    # 删除缺陷检测结果的报告
    def Delete_Detection_Report(self, report_ids: str):
        try:
            if len(report_ids) == 0:
                print("没有提供所要删除的报告ID")
                return
            placeholders = ",".join(["%s"] * len(report_ids))
            sql = f"""
            DELETE FROM Detection_reports
            WHERE id IN ({placeholders})
            """
            self.cursor.execute(sql, report_ids)
            self.conn.commit()
            # print("删除成功！")
        except mysql.connector.Error as e:
            print(f"数据库报错: {e}")
        except Exception as e:
            print(f"发生错误: {e}")

    # 批量更新缺陷检测结果数据。也就是对多条数据的同一个属性值进行更新
    def Batch_Update_Detection_Results(self, result_ids: list, update_fields: dict):
        try:
            if not result_ids or not isinstance(result_ids, list):
                print("没有提供需要更新的 ID 列表")
                return

            if not update_fields or not isinstance(update_fields, dict):
                print("没有提供需要更新的字段")
                return

            # 构造 SET 子句
            set_clause = []
            params = []
            for field, value in update_fields.items():
                if field not in self.Detection_results_parm:
                    print(f"字段 {field} 不在可更新范围内")
                    continue
                set_clause.append(f"{field} = %s")
                params.append(value)

            if not set_clause:
                print("没有有效的字段可以更新")
                return

            # 构造完整的 SQL 语句
            placeholders = ', '.join(['%s'] * len(result_ids))
            sql = f"""
            UPDATE Detection_results
            SET {', '.join(set_clause)}
            WHERE id IN ({placeholders})
            """
            params.extend(result_ids)

            # 执行 SQL 语句
            self.cursor.execute(sql, params)
            self.conn.commit()
            # print(f"批量更新成功，更新了 {self.cursor.rowcount} 条记录！")

        except mysql.connector.Error as e:
            print(f"数据库错误: {e}")
        except Exception as e:
            print(f"操作数据时发生错误: {e}")

    # 批量更新检测结果数据
    def Batch_Update_Defect_Details(self, defect_ids: list, update_fields: dict):
        try:
            if not defect_ids or not isinstance(defect_ids, list):
                print("没有提供需要更新的 ID 列表")
                return

            if not update_fields or not isinstance(update_fields, dict):
                print("没有提供需要更新的字段")
                return

            set_clause = []
            params = []
            for field, value in update_fields.items():
                if field not in self.Defect_details_parm:
                    print(f"字段 {field} 不在可更新范围内")
                    continue
                set_clause.append(f"{field} = %s")
                params.append(value)

            if not set_clause:
                print("没有有效的字段可以更新")
                return

            placeholders = ', '.join(['%s'] * len(defect_ids))
            sql = f"""
            UPDATE Defect_details
            SET {', '.join(set_clause)}
            WHERE id IN ({placeholders})
            """
            params.extend(defect_ids)

            self.cursor.execute(sql, params)
            self.conn.commit()
            # print(f"批量更新成功，更新了 {self.cursor.rowcount} 条记录！")

        except mysql.connector.Error as e:
            print(f"数据库错误: {e}")
        except Exception as e:
            print(f"操作数据时发生错误: {e}")

    # 批量更新标注数据
    def Batch_Update_Annotation_Data(self, anno_ids: list, update_fields: dict):
        try:
            if not anno_ids or not isinstance(anno_ids, list):
                print("没有提供需要更新的 ID 列表")
                return
            if not update_fields or not isinstance(update_fields, dict):
                print("没有提供需要更新的字段")
                return

            set_clause = []
            params = []
            for field, value in update_fields.items():
                if field not in self.Annotation_data_parm:
                    print(f"字段 {field} 不在可更新范围内")
                    continue
                set_clause.append(f"{field} = %s")
                params.append(value)

            if not set_clause:
                print("没有有效的字段可以更新")
                return

            placeholders = ', '.join(['%s'] * len(anno_ids))
            sql = f"""
            UPDATE Annotation_data
            SET {', '.join(set_clause)}
            WHERE id IN ({placeholders})
            """
            params.extend(anno_ids)

            self.cursor.execute(sql, params)
            self.conn.commit()
            # print(f"批量更新成功，更新了 {self.cursor.rowcount} 条记录！")

        except mysql.connector.Error as e:
            print(f"数据库错误: {e}")
        except Exception as e:
            print(f"操作数据时发生错误: {e}")

    # 批量更新检测报告数据
    def Batch_Update_Detection_Reports(self, report_ids: list, update_fields: dict):
        try:
            if not report_ids or not isinstance(report_ids, list):
                print("没有提供需要更新的 ID 列表")
                return
            if not update_fields or not isinstance(update_fields, dict):
                print("没有提供需要更新的字段")
                return

            set_clause = []
            params = []
            for field, value in update_fields.items():
                if field not in self.Detection_reports_parm:
                    print(f"字段 {field} 不在可更新范围内")
                    continue
                set_clause.append(f"{field} = %s")
                params.append(value)

            if not set_clause:
                print("没有有效的字段可以更新")
                return
            placeholders = ', '.join(['%s'] * len(report_ids))
            sql = f"""
            UPDATE Detection_reports
            SET {', '.join(set_clause)}
            WHERE id IN ({placeholders})
            """
            params.extend(report_ids)

            self.cursor.execute(sql, params)
            self.conn.commit()
            # print(f"批量更新成功，更新了 {self.cursor.rowcount} 条记录！")

        except mysql.connector.Error as e:
            print(f"数据库错误: {e}")
        except Exception as e:
            print(f"操作数据时发生错误: {e}")

    # 根据所选择的defect_id， 从数据库中查询数据并将这些数据进行进一步提取，得到 缺陷类型、缺陷面积、缺陷的时间分布等信息
    def Infer_Result_Extra(self, defect_ids: list):
        # print(defect_ids)
        if not defect_ids or not isinstance(defect_ids, list):
            print("没有提供需要的 ID 列表")
            return

        place_holders = ', '.join(['%s'] * len(defect_ids))
        sql = f"""
        SELECT defect_type, x_center, y_center, width, height, area_proportion, upload_time
        FROM Defect_details WHERE id IN ({place_holders})
        """
        self.cursor.execute(sql, defect_ids)
        results = self.cursor.fetchall()

        if not results:
            print('未查找到数据\n')
            return
        # print(results)

        defect_data = []
        time_list = []
        for result in results:
            defect_type, x_center, y_center, width, height, area_proportion, upload_time = result
            defect_dict = {'defect_type': defect_type, 'x_center': x_center, 'y_center': y_center, \
                           'width': width, 'height': height, 'area_proportion': area_proportion}
            defect_data.append(defect_dict)
            time_list.append(upload_time)

        # print(defect_data)
        # 获取 defect_data 信息
        (defect_types, defect_type_cnt, defect_distribution_avg, defect_avg_dimensions_avg, defect_center_std,
         defect_avg_area_proportion, defect_area_proportion_std) = extract_defect_info(defect_data)

        # 获取缺陷检测的时间分布信息
        time_list = [upload_time.strftime('%Y-%m-%d %H:%M:%S') for upload_time in time_list]
        # print(time_list)
        time_msg = time_msg_extra(time_list)
        if defect_types is not None:
            # print(f"缺陷类别: {defect_types}")
            # print(f'每种缺陷出现的次数: {defect_type_cnt}')
            # print(f"每种缺陷的分布区域 (平均中心点): {defect_distribution_avg}")
            # print(f"每种缺陷的平均长宽: {defect_avg_dimensions_avg}")
            # print(f"每种缺陷中心点的标准差: {defect_center_std}")
            # print(f"每种缺陷的分布区域 (平均面积比例): {defect_avg_area_proportion}")
            # print(f"每种缺陷的分布区域 (面积比例标准差): {defect_area_proportion_std}")
            # print(f"不同时间区间内缺陷的出现情况：{time_msg}")
            return [defect_types, defect_type_cnt, defect_distribution_avg, defect_avg_dimensions_avg,
                    defect_center_std, defect_avg_area_proportion, defect_area_proportion_std,
                    time_msg]
        else:
            print("读取文件失败")
            return None
        #
        # except mysql.connector.Error as e:
        #     print(f"数据库错误: {e}")
        #     return None
        # except Exception as e:
        #     print(f"操作数据时发生错误: {e}")
        #     return None

    def Defect_Result_Visualize(self, defect_ids: list):
        try:
            if not defect_ids or not isinstance(defect_ids, list):
                print("没有提供需要更新的 ID 列表")
                return

            print(defect_ids)
            place_holders = ', '.join(['%s'] * len(defect_ids))
            sql = f"""
            SELECT defect_type, x_center, y_center, width, height, area_proportion, upload_time
            FROM Defect_details WHERE detection_result_id IN ({place_holders})
            """
            self.cursor.execute(sql, tuple(defect_ids))
            results = self.cursor.fetchall()

            if not results:
                print('未查找到数据\n')
                return

            time_list = []
            defect_type_cnt = {}  # 统计每种缺陷类型出现的次数
            defect_points = {}  # 统计每种缺陷出现的位置
            defect_area = {}  # 统计每种缺陷的面积比例
            for result in results:
                defect_type, x_center, y_center, width, height, area_proportion, upload_time = result

                if defect_type not in defect_type_cnt:
                    defect_type_cnt[defect_type] = 1
                else:
                    defect_type_cnt[defect_type] += 1

                if defect_type not in defect_points:
                    defect_points[defect_type] = [{x_center, y_center}]
                else:
                    defect_points[defect_type].append({x_center, y_center})

                if defect_type not in defect_area:
                    defect_area[defect_type] = [area_proportion]
                else:
                    defect_area[defect_type].append(area_proportion)

                time_list.append(upload_time)

            # 获取缺陷检测的时间分布信息
            time_list = [upload_time.strftime('%Y-%m-%d %H:%M:%S') for upload_time in time_list]

            time_msg = time_msg_extra(time_list, interval_size=86400)
            save_path = [plot_defect_type_pie_chart(defect_type_cnt, save_path='缺陷类型分布图'),
                         plot_defect_center_distribution(defect_points, save_path='缺陷中心分布图'),
                         plot_defect_area_proportion_distribution(defect_area, save_path='缺陷面积占比分布图'),
                         plot_defect_time_distribution(time_msg, save_path='缺陷时间分布图')]

            return save_path


        except mysql.connector.Error as e:
            print(f"数据库错误: {e}")
            return None
        except Exception as e:
            print(f"操作数据时发生错误: {e}")
            return None

    def Query_Table_Data(self, table_name):
        """查询指定表的数据"""
        query_map = {
            "Detection_results": "SELECT id, image_name, image_type, upload_time FROM Detection_results",
            "Annotation_data": "SELECT id, image_name, image_type, upload_time FROM Annotation_data",
            "Detection_reports": "SELECT id, report_file_name, report_file_type, report_time FROM Detection_reports",
            "Defect_details": "SELECT id, result_image_name, detection_result_id, defect_type, x_center, y_center, width, height, area_proportion, upload_time FROM Defect_details",
            "Model_info": "SELECT id, model_name, model_type, upload_time FROM Model_info",
        }
        query = query_map.get(table_name, "")
        if not query:
            return []

        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"数据库查询失败: {e}")
            return []

    def get_image_id(self, image_names: list):
        if not image_names:
            return []
        placeholders = ','.join(['%s'] * len(image_names))
        sql = f"""
                    SELECT id
                    FROM Detection_results
                    WHERE image_name IN ({placeholders})
                """
        self.cursor.execute(sql, image_names)
        results = self.cursor.fetchall()
        return [row[0] for row in results] if results else []


if __name__ == "__main__":
    Create_Database('./build.sql', 'localhost', 'root', '200407', database_name='defection_db')

    db = DataBase("localhost", "root", "200407", "defection_db",
                  mysql_path=r'C:\Program Files\MySQL\MySQL Server 5.7\bin\mysql.exe',
                  mysqldump_path=r'C:\Program Files\MySQL\MySQL Server 5.7\bin\mysqldump.exe')
    # db.Defect_Result_Visualize([i for i in range(24, 50)])
    # db.Delete_Defect_Details([i for i in range(37, 42)])

    # db.Batch_Update_Defect_Details([i for i in range(10, 14)], {"upload_time": "2025-03-20 20:00:00"})

    # db.Insert_Detected_Details(1, '1.png' ,'./03db6bbc3.txt')
    # db.Insert_Detected_Details(2, '2.png' ,'./1ea493a4f.txt')
    # db.Insert_Detected_Details(3, '3.png' ,'./1f9b8e2e6.txt')
    # db.Insert_Detected_Details(4, '4.png' ,'./pitted_surface_1.txt')

