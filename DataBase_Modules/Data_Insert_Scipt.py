from DataBase import *

if __name__ == '__main__' :
    db = DataBase("localhost", "root", "200407", "defection_db",
                  mysql_path=r'C:\Program Files\MySQL\MySQL Server 5.7\bin\mysql.exe',
                  mysqldump_path=r'C:\Program Files\MySQL\MySQL Server 5.7\bin\mysqldump.exe')
    
    # 批量插入Annotation_data
    anno_path = './Annotation/txt/'
    for path in os.listdir(anno_path) :
        name = path.split('/')[-1].split('.')[0]
        txt_path = f'./Annotation/txt/{name}.txt'
        image_path = f'./Annotation/src/{name}.jpg'
        anno_image_path = f'./Annotation/anno/{name}.jpg'
        db.Insert_Annotation_Data(image_path, anno_image_path, txt_path)
    
    # 插入检测报告，犯懒了先用txt替代。。。
    for path in os.listdir(anno_path) :
        name = path.split('/')[-1].split('.')[0]
        txt_path = f'./Annotation/txt/{name}.txt'
        db.Insert_Detection_Report(txt_path)


    detect_result_path = './Detection_results/txt'
    
    # 插入检测结果图片
    for path in os.listdir(detect_result_path):
        name = path.split('/')[-1].split('.')[0]
        txt_path = f'./Detection_results/txt/{name}.txt'
        image_path = f'./Detection_results/image/{name}.jpg'
        db.Insert_Detected_Image_Data(image_path, txt_path)
    
    # 插入检测结果详细数据，那些详细数据txt都是engine_infer推理生成的
    cnt = 1
    for path in os.listdir(detect_result_path):
        name = path.split('/')[-1].split('.')[0]
        txt_path = f'./Detection_results/txt/{name}.txt'
        db.Insert_Detected_Details(cnt, result_image_name=name, txt_path=txt_path)
        cnt = cnt + 1
    

    