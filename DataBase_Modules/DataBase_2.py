import mysql.connector
import os
from datetime import datetime
import subprocess


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

        command = [
            r'C:\Program Files\MySQL\MySQL Server 5.7\bin\mysql.exe',
            "-h", host,
            "-u", user,
            f"-p{password}",
        ]

        # 执行命令并从 SQL 文件中创建数据库
        result = subprocess.run(command, input=sql_content, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                shell=True)

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
        try:
            self.conn = mysql.connector.connect(**self.DB_CONFIG)
            self.cursor = self.conn.cursor()
        except mysql.connector.Error as e:
            print(f"无法连接到MySQL数据库，报错: {e}")
            self.conn = None
            self.cursor = None



    # 重新连接数据库
    def Reconnect_Database(self):
        try:
            self.conn = mysql.connector.connect(**self.DB_CONFIG)
            self.cursor = self.conn.cursor()
        except mysql.connector.Error as e:
            print(f"法连接到MySQL数据库，报错: {e}")
            self.conn = None
            self.cursor = None

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

    # 插入缺陷检测的结果图片和数据
    # 包括：检测结果图片、图片名称、图片类型、缺陷掩码、缺陷类型、缺陷面积占比
    def Insert_Detected_Image_Data(self, image_path: str, defect_mask_path: str,
                                   defect_type: str, defect_proportion: str):
        try:
            image_name = image_path.split("/")[-1]
            image_type = image_name.split(".")[-1]

            # 读取二进制的图片数据
            image_data = self.read_binary_data(image_path)
            if image_data is None:
                print(f"读取图片{image_name}数据失败！")
                return

            defect_mask_name = defect_mask_path.split("/")[-1]
            defect_mask = self.read_binary_data(defect_mask_path)
            if defect_mask is None:
                print(f"读取{defect_mask_name}数据失败！")
                return

            sql = """
            INSERT INTO detection_results (
                image_name, image_type, image_data, defect_mask, upload_time, defect_type, defect_area_proportion
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s
            ) ON DUPLICATE KEY UPDATE
                image_type = VALUES(image_type),
                image_data = VALUES(image_data),
                defect_mask = VALUES(defect_mask),
                upload_time = VALUES(upload_time),
                defect_type = VALUES(defect_type),
                defect_area_proportion = VALUES(defect_area_proportion)
            """
            self.cursor.execute(sql, (image_name, image_type, image_data, defect_mask, \
                                      datetime.now().strftime("%Y-%m-%d_%H:%M:%S"), defect_type, defect_proportion))
            self.conn.commit()
            print(f"图片数据{image_name}插入成功！")

        except mysql.connector.Error as e:
            print(f"数据库错误: {e}")
        except Exception as e:
            print(f"操作数据时发生错误: {e}")

    # 插入标注缺陷区域的数据，后期用作训练模型的数据
    # 包括：图片名称、图片类型、图片数据、缺陷掩码、缺陷信息
    def Insert_Annotation_Data(self, image_path: str, defect_mask_path: str,
                               defect_msg: str):
        try:
            image_name = image_path.split('/')[-1]
            image_type = image_name.split(".")[-1]
            image_data = self.read_binary_data(image_path)
            if image_data is None:
                print(f"读取{image_name}数据失败！")
                return
            defect_mask_name = defect_mask_path.split('/')[-1]
            defect_mask = self.read_binary_data(defect_mask_path)
            if defect_mask is None:
                print(f"读取{defect_mask_name}数据失败！")
                return

            sql = """
            INSERT INTO annotation_data (
                image_name, image_type, image_data, defect_mask, defect_msg, upload_time
            ) VALUES (
                %s, %s, %s, %s, %s, %s
            ) ON DUPLICATE KEY UPDATE
                image_name = VALUES(image_name),
                image_type = VALUES(image_type),
                image_data = VALUES(image_data),
                defect_mask = VALUES(defect_mask),
                defect_msg = VALUES(defect_msg),
                upload_time = VALUES(upload_time)
            """
            self.cursor.execute(sql, (image_name, image_type, image_data, defect_mask, \
                                      defect_msg, datetime.now().strftime("%Y-%m-%d_%H:%M:%S")))
            self.conn.commit()
            print(f'图片数据{image_name}插入成功！')

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
            INSERT INTO detection_reports (
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
            print(f"检测报告{report_name}插入成功！")

        except mysql.connector.Error as e:
            print(f"数据库错误: {e}")
        except Exception as e:
            print(f"操作数据时发生错误: {e}")

    # 查询缺陷检测的结果数据，支持一次查询多条数据，查询过程通过id来查询
    def Get_Detected_Image(self, image_ids: list, save_path: str):
        try:
            if not os.path.exists(save_path):
                os.makedirs(save_path)

            placeholders = ', '.join(['%s'] * len(image_ids))
            sql = f"""
            SELECT image_name, image_type, image_data, defect_mask, defect_type, defect_area_proportion
            FROM detection_results
            WHERE id IN ({placeholders})
            """
            self.cursor.execute(sql, image_ids)
            results = self.cursor.fetchall()

            if not results:
                print('未找到图片数据')
                return

            for result in results:
                # 查询的每一条结果
                image_name, image_type, image_data, defect_mask, defect_type, defect_area_proportion = result
                image_file_path = f'{save_path}/{image_name}'
                with open(image_file_path, "wb") as file:
                    file.write(image_data)
                mask_file_path = f'{save_path}/{image_name.split(f".{image_type}")[0]}_mask.png'
                with open(mask_file_path, "wb") as file:
                    file.write(defect_mask)
                print(f'defect_type: {defect_type}')
                print(f'defect_area_proportion: {defect_area_proportion}')

        except mysql.connector.Error as e:
            print(f'数据库错误: {e}')
        except Exception as e:
            print(f'错误: {e}')

    # 查询缺陷检测的报告文件，支持一次查询多条数据，查询过程通过id来查询
    def Get_Report_File(self, file_ids: list, save_path: str):
        try:
            if not os.path.exists(save_path):
                os.makedirs(save_path)
            placeholders = ', '.join(['%s'] * len(file_ids))
            sql = f"""
                SELECT report_file_name, report_file_type, report_file
                FROM detection_reports
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
                print(f"报告文件 {file_name} 保存成功。")
        except mysql.connector.Error as e:
            print(f"数据库错误: {e}")
        except Exception as e:
            print(f"发生错误: {e}")

    # 查询标注的数据
    def Get_Annotation_Data(self, image_ids: list, save_path: str):
        try:
            if not os.path.exists(save_path):
                os.makedirs(save_path)
            placeholders = ",".join(["%s"] * len(image_ids))
            sql = f"""
            SELECT image_name, image_type, image_data, defect_mask, defect_msg
            FROM annotation_data
            WHERE id IN ({placeholders})
            """
            self.cursor.execute(sql, image_ids)
            results = self.cursor.fetchall()

            if not results:
                print("未找到指定 ID 的图片")
                return
            for result in results:
                image_name, image_type, image_data, defect_mask, defect_msg = result
                image_path = f"{save_path}/{image_name}"
                with open(image_path, "wb") as file:
                    file.write(image_data)
                mask_path = f'{save_path}/{image_name.split(".")[0]}_mask.{image_type}'
                with open(mask_path, "wb") as file:
                    file.write(defect_mask)
                print(defect_msg)
                print(f'图片已保存为 {image_name}, 缺陷标注已保存为 {mask_path}')

        except mysql.connector.Error as e:
            print(f"数据库错误: {e}")
        except Exception as e:
            print(f"发生错误: {e}")

    # 对数据库进行备份，备份的位置在：backup_file , eg: ./backup/data.sql
    def Backup_DataBase(self, backup_file: str):
        try:
            command = [
                # 注意，这边需要填写的是mysqldump的安装路径
                self.mysqldump_path,
                "-h", self.DB_CONFIG['host'],
                "-u", self.DB_CONFIG['user'],
                f"-p{self.DB_CONFIG['password']}",
                self.DB_CONFIG['database']
            ]

            backup_dir = os.path.dirname(backup_file)

            if backup_dir and not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
                print(f"创建备份目录: {backup_dir}")

            with open(backup_file, 'w') as file:
                subprocess.run(command, stdout=file, stderr=subprocess.PIPE, check=True, shell=True)

            print(f"备份数据完成，备份文件保存在: {backup_file}")

        except subprocess.CalledProcessError as e:
            print(f"备份数据时出错: {e.stderr.decode('utf-8')}")
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

    # 删除检测结果图像
    def Delete_Detected_Image_Data(self, image_ids: str):
        try:
            if len(image_ids) == 0:
                print("没有提供所要删除的图像ID")
                return

            placeholders = ",".join(["%s"] * len(image_ids))
            sql = f"""
            DELETE FROM detection_results
            WHERE id IN ({placeholders})
            """
            self.cursor.execute(sql, image_ids)
            self.conn.commit()
            print("删除成功！")

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
            DELETE FROM annotation_data
            WHERE id IN ({placeholders})
            """
            self.cursor.execute(sql, image_ids)
            self.conn.commit()
            print("删除成功！")

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
            DELETE FROM detection_reports
            WHERE id IN ({placeholders})
            """
            self.cursor.execute(sql, report_ids)
            self.conn.commit()
            print("删除成功！")
        except mysql.connector.Error as e:
            print(f"数据库报错: {e}")
        except Exception as e:
            print(f"发生错误: {e}")


    def Query_Table_Data(self, table_name):
        """查询指定表的数据"""
        query_map = {
            "Detection_results": "SELECT id, image_name, image_type, defect_type, defect_area_proportion, upload_time FROM Detection_results",
            "Annotation_data": "SELECT id, image_name, image_type, upload_time FROM Annotation_data",
            "Detection_reports": "SELECT id, report_file_name, report_file_type, report_time FROM Detection_reports"
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

    def Query_All_Data(self):
        """查询数据库中的所有数据"""
        query = "SELECT id, image_name, image_type, defect_type, defect_area_proportion FROM detection_results"
        self.cursor.execute(query)
        return self.cursor.fetchall()


if __name__ == "__main__":
    Create_Database('./build.sql', 'localhost', 'root', '200407', 'vehicle_inspection')
    db = DataBase("localhost", "root", "200407", "vehicle_inspection",
                  mysql_path=r'C:\Program Files\MySQL\MySQL Server 5.7\bin\mysql.exe',
                  mysqldump_path=r'C:\Program Files\MySQL\MySQL Server 5.7\bin\mysqldump.exe')

    db.Restore_Database('./backup/data.sql')

    # db.Delete_Detection_Report([1, 2, 3])
    # db.Delete_Detected_Image_Data([12])

    # db.Insert_Detected_Image_Data("./123.png", "./123.png", "crack", "crack:0.5")
    # db.Insert_Detected_Image_Data("./1234.png", "./123.png", "crack", "crack:0.5")
    # db.Insert_Annotation_Data("./123.png", "./123.png", "dent:3242 12 4324 25;crack:2342 23 2342 23")
    # db.Insert_Detection_Report("Report.md")

    # db.release_database()
