import mysql.connector
from mysql.connector import Error

def create_database_and_tables(host, user, password, database_name):
    """创建数据库和所有数据表"""
    try:
        # 1. 连接MySQL服务器（不指定数据库）
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )
        cursor = connection.cursor()
        
        print(f"✅ 成功连接到MySQL服务器")

        # 2. 创建数据库
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{database_name}`")
        print(f"✅ 数据库 {database_name} 创建/验证成功")

        # 3. 切换到新数据库
        cursor.execute(f"USE `{database_name}`")
        
        # 4. 创建所有表
        # 4.1 创建Detection_results表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Detection_results (
            id INT AUTO_INCREMENT PRIMARY KEY,
            image_name VARCHAR(64) NOT NULL UNIQUE,
            image_type VARCHAR(10) NOT NULL,
            image_data LONGBLOB NOT NULL,
            defect_result LONGBLOB NOT NULL,
            upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # 4.2 创建Defect_details表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Defect_details (
            id INT AUTO_INCREMENT PRIMARY KEY,
            result_image_name VARCHAR(50) NOT NULL,
            detection_result_id INT NOT NULL,
            defect_type VARCHAR(50) NOT NULL,
            x_center FLOAT NOT NULL,
            y_center FLOAT NOT NULL,
            width FLOAT NOT NULL,
            height FLOAT NOT NULL,
            area_proportion FLOAT NOT NULL,
            upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (detection_result_id) REFERENCES Detection_results(id) ON DELETE CASCADE
        )
        """)
        
        # 4.3 创建Annotation_data表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Annotation_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            image_name VARCHAR(64) NOT NULL UNIQUE,
            image_type VARCHAR(10) NOT NULL,
            image_data LONGBLOB NOT NULL,
            annotation_image LONGBLOB NOT NULL,
            yolo_anno LONGBLOB,
            upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # 4.4 创建Detection_reports表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Detection_reports (
            id INT AUTO_INCREMENT PRIMARY KEY,
            report_file_name VARCHAR(255) NOT NULL,
            report_file_type VARCHAR(50) NOT NULL,
            report_file LONGBLOB NOT NULL,
            report_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # 4.5 创建Model_info表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Model_info (
            id INT AUTO_INCREMENT PRIMARY KEY,
            model_name VARCHAR(255) NOT NULL,
            model_type VARCHAR(50) NOT NULL,
            model_path VARCHAR(50) NOT NULL,
            remark VARCHAR(1024),
            upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        print("✅ 所有表创建成功")
        
        # 5. 验证表结构
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"\n📊 数据库中的表: {[table[0] for table in tables]}")
        
    except Error as e:
        print(f"❌ 错误: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("⏹️ MySQL连接已关闭")

if __name__ == "__main__":
    # 配置参数
    config = {
        "host": "localhost",
        "user": "root",
        "password": "123456",  # 替换为你的密码
        "database_name": "new_table"  # 数据库名称
    }
    
    print("="*50)
    print(f"开始创建数据库 {config['database_name']} 和表结构...")
    print("="*50)
    
    create_database_and_tables(**config)
    
    print("\n👉 验证命令:")
    print(f"mysql -u {config['user']} -p{config['password']} -e 'SHOW DATABASES; USE {config['database_name']}; SHOW TABLES;'")