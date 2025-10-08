import cv2
from PIL import Image, ImageTk
from datetime import datetime

'''
    用于实现图像采集的模块，主要是对摄像头对象的管理
    设计的功能包括：打开/关闭摄像头、采集图像、保存图像文件、获取图像帧等
'''


class Camera:
    def __init__(self):
        self.is_camera_open = False  # 是否打开摄像头
        self.cap = None  # 摄像头对象

    # 控制打开摄像头
    def open_camera(self, index=0):
        '''
            参数：
            index: 摄像头索引号，默认为0，笔记本电脑自带的摄像头的索引号为0，外接的为: 1、2、3 ...
        '''
        if self.is_camera_open:
            assert False, f"摄像头{index} 已打开"
        else:
            self.cap = cv2.VideoCapture(index=index)

            if not self.cap.isOpened():
                assert False, f"错误：无法打开摄像头{index}, 请检查设备是否被占用或驱动是否正确安装。"
                print(f"错误：无法打开摄像头{index}, 请检查设备是否被占用或驱动是否正确安装。")

                return

            self.is_camera_open = True
            print(f"摄像头{index} 打开成功")

    # 用于获得摄像头采集的每一帧图像
    def read_camera_img(self):
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                return ret, frame
            else:
                print("无法读取摄像头图像")
                return None
        else:
            if not self.is_camera_open:
                assert False, "摄像头未打开"
            if not self.cap:
                assert False, "摄像头对象未初始化"
            return None

            # 获得摄像头采集的每一帧图像，用于同步摄像头所拍摄的内容

    def show_capture_frame(self):
        ret, frame = self.read_camera_img()
        if ret:
            return frame

        return None

    # 用于截取并保存摄像头所拍摄的图像（一张）
    def save_capture_image(self, image_name=None):
        ret, frame = self.read_camera_img()
        if ret:
            '''
                当没有指定保存图片的文件名
                使用当前的时间来作为文件名：年-月-日_时-分-秒
            '''
            file_name = (
                        "./images/" + image_name + '.png') if image_name else f'./{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.png'
            cv2.imwrite(file_name, frame)
            print(f"图片保存成功: {file_name}")
            return file_name

        assert False, f'图片无法保存，请检查文件名或路径是否正确'

    # 关闭摄像头，释放资源
    def close_camera(self):
        if self.cap:
            self.cap.release()
            self.is_camera_open = False
            print("摄像头已关闭")


if __name__ == "__main__":
    camera = Camera()
    # camera.open_camera()

    for i in range(10):

        op = (int)(input("请输入操作：\n1. 打开摄像头\n2. 关闭摄像头\n3. 读取一帧图像并显示\n4. 保存所拍摄到的图像\n"))
        if op == 1:
            camera.open_camera()
        elif op == 2:
            camera.close_camera()
        elif op == 3:
            # 这边使用循环，来持续得到摄像头的画面
            while True:
                img = camera.show_capture_frame()
                cv2.imshow('Camera', img)

                '''
                    如果想要在采集过程中截取所拍摄的图片，可以修改ord('*')为任意键
                    就可以通过按下对应按键并进行图片截取
                '''
                if cv2.waitKey(1) & 0xFF == ord('t'):
                    file_name = input("请输入存的文件名：")
                    camera.save_capture_image(file_name)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    cv2.destroyAllWindows()
                    break
        elif op == 4:
            file_name = input("请输入存的文件名：")
            camera.save_capture_image(file_name)
        else:
            break

    camera.close_camera()
    print("摄像头已关闭")
