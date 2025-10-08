from DataBase import *
DB_CONFIG = {
            'host': 'localhost',
            'user': 'root',
            'password': '123456',
            'database': 'database',
        }

def Create_Database(sql_file_path: str) :
        try : 
            if not os.path.exists(sql_file_path) :
                print(f"文件不存在: {sql_file_path}")
                return
            
            command = [
                '/usr/bin/mysql',
                "-h", DB_CONFIG['host'],
                "-u", DB_CONFIG['user'],
                f"-p{DB_CONFIG['password']}",
            ]
            # 执行命令并从 SQL 文件中创建数据库
            with open(sql_file_path, 'r', encoding='utf-8') as file:
                result = subprocess.run(command, stdin=file, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode != 0:
                print(f"创建数据库失败，错误信息:\n{result.stderr}")
            else:
                print(f"数据库创建成功，SQL 文件: {sql_file_path}")
        except subprocess.CalledProcessError as e :
            print(f"执行命令失败，错误信息:\n{e.output}")
        except Exception as e :
            print(f"发生错误: {e}")

if __name__ == "__main__" :
    # Create_Database('./build.sql')
    db = DataBase("localhost", "root", "123456", "vehicle_inspection",
                mysql_path=r'C:\Program Files\MySQL\MySQL Server 5.7\bin\mysql.exe',
                mysqldump_path=r'C:\Program Files\MySQL\MySQL Server 5.7\bin\mysqldump.exe')
    
    # db.Get_Annotation_Data([1], './saved_ann')
    # db.Get_Report_File([1, 2], './saved_files')
    # db.Get_Detected_Image([12, 13], './saved_images')
    # db.Restore_Database('./backup/data.sql')
    
    # k = DataBase("localhost", "root", "123456", "vehicle_inspection")