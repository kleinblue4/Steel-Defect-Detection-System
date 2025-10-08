# 钢材缺陷智能检测系统

本项目是一个基于 **YOLOV11** 的缺陷检测系统，基于 PyTorch、TensorRT 和 PyQt 框架开发。目前项目支持本地和 Docker 镜像部署，具体部署和使用流程参照以下内容：

## Docker运行项目系统

本项目已构建Docker镜像，并发布到阿里云，可以将镜像pull到本地，并配置好相关软硬件后运行。
具体流程为：

- 在终端运行： `docker pull crpi-r37s2gzadg742ivt.cn-shanghai.personal.cr.aliyuncs.com/yunzhoudanxin/defect:latest`
- 拉取镜像之后，运行 ：`docker images`  查看是否拉取到镜像。
- 运行镜像容器：首先运行 `xhost +local:docker` 。确保docker容器内可以打开QT界面。
- 随后运行容器： `docker run -it --device=/dev/video0 -e DISPLAY=unix$DISPLAY --gpus all -v /tmp/.X11-unix:/tmp/.X11-unix [ your_image_name ]`
- 进入容器后，执行：`python pyqt_.py` 进入系统界面。

## 本地运行项目系统

若要在本地运行项目系统，请先创建 python 虚拟环境，建议使用conda创建并维护

创建 conda 环境之后，安装 requirement.txt 

运行系统之前，需要先创建所需的数据库，在 conda 环境下，运行 `build_sql.py` 文件，创建MySQL数据库

随后运行 `pyqt_.py` 文件，开始运行系统


