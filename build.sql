CREATE DATABASE IF NOT EXISTS {database_name};
USE {database_name};

-- 存储缺陷检测后的图片数据
CREATE TABLE IF NOT EXISTS Detection_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    image_name VARCHAR(64) NOT NULL UNIQUE,
    image_type VARCHAR(10) NOT NULL,                  -- 图片类型 (如 jpg, png)
    image_data LONGBLOB NOT NULL,                     -- 存储 二进制图片数据
    defect_result LONGBLOB NOT NULL,                  -- 存储 缺陷检测结果图
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP   -- 上传时间
);
-- 举例：
-- id  image_name   image_type  image_data  defect_result   upload_time
-- 1   result1.jpg  jpg         0x1234...   0x1234.....     2023-07-01 12:00:00 


-- 存储每个缺陷的具体信息,注意：所有的坐标和高宽都是归一化之后的结果
CREATE TABLE IF NOT EXISTS Defect_details (
    id INT AUTO_INCREMENT PRIMARY KEY,
    result_image_name VARCHAR(50) NOT NULL,           -- 对应 Detection_results 表的 image_name， 但是不设置外键约束
    detection_result_id INT NOT NULL,                 -- 关联到 Detection_results 表的 id
    defect_type VARCHAR(50) NOT NULL,                 -- 缺陷类型
    x_center FLOAT NOT NULL,                          -- 归一化的缺陷中心点 x 坐标
    y_center FLOAT NOT NULL,                          -- 归一化的缺陷中心点 y 坐标
    width FLOAT NOT NULL,                             -- 归一化的缺陷宽度
    height FLOAT NOT NULL,                            -- 归一化的缺陷高度
    area_proportion FLOAT NOT NULL,                   -- 缺陷区域占比
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 上传时间
    FOREIGN KEY (detection_result_id) REFERENCES Detection_results(id) ON DELETE CASCADE
);
-- 举例：
-- id  result_image_name   detection_result_id  defect_type  x_center   y_center   width  height   area_proportion  upload_time
-- 1   1.jpg               1                    crack         0.35      0.25       0.05    0.1     0.005            2023-07-01 12:00:00

-- 存储所标注的图片数据
CREATE TABLE IF NOT EXISTS Annotation_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    image_name VARCHAR(64) NOT NULL UNIQUE,
    image_type VARCHAR(10) NOT NULL,                 -- 图片类型 (如 jpg, png)
    image_data LONGBLOB NOT NULL,                    -- 存储图片数据
    annotation_image LONGBLOB NOT NULL,              -- 存储 二进制缺陷掩码数据
    yolo_anno LONGBLOB,                              -- 存储缺陷信息txt , 最长16MB
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- 上传时间
);
-- 举例：
-- id  image_name  image_type  image_data  defect_mask  yolo_anno   upload_time
-- 1   anno1.jpg   jpg         0x1234...   0x1234.....  anno.txt    2023-07-01 12:00:00


-- 存储检测结果报告
CREATE TABLE IF NOT EXISTS Detection_reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    report_file_name VARCHAR(255) NOT NULL,  -- 存储文件名称
    report_file_type VARCHAR(50) NOT NULL,   -- 文件类型 (如 pdf, docx)
    report_file LONGBLOB NOT NULL,           -- 存储二进制文件数据
    report_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 存储模型的信息，包括名称、路径、类型和备注
CREATE TABLE IF NOT EXISTS Model_info (
    id INT AUTO_INCREMENT PRIMARY KEY,                 -- 自增主键
    model_name VARCHAR(255) NOT NULL,                  -- 模型名称
    model_type VARCHAR(50) NOT NULL,                   -- 模型类型
    model_path VARCHAR(50) NOT NULL,                   -- 模型路径
    remark VARCHAR(1024),                              -- 备注信息
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- 举例：
-- id  model_name  model_type  model_path          remark             upload_time
-- 1   best        pt          ./weights/best.pt   用于缺陷检测的模型    2023-07-01 12:00:00
