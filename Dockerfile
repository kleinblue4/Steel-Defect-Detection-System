# 1. 使用带CUDA和cuDNN的基础镜像（适配11.8/8.7）
FROM nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04


# 2. 环境变量
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# 3. 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    git \
    wget \
    unzip \
    pkg-config \
    libgtk-3-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libtbb2 \
    libtbb-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libx11-dev \
    qtbase5-dev \
    python3-dev \
    ca-certificates \
    mysql-server \
    mysql-client \
    libmysqlclient-dev \
    fonts-wqy-zenhei \
    fonts-wqy-microhei \
    ttf-wqy-zenhei \
    ttf-wqy-microhei \
    xfonts-wqy \
    libqt5core5a \
    libqt5gui5 \
    libqt5widgets5 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 4. 安装 Miniconda
COPY Miniconda3-latest-Linux-x86_64.sh /tmp/miniconda.sh
RUN bash /tmp/miniconda.sh -b -p /opt/conda && \
    rm /tmp/miniconda.sh
ENV PATH="/opt/conda/bin:$PATH"


# 拷贝环境配置文件并创建 Conda 环境
COPY environment.yaml /tmp/environment.yaml
RUN conda env create -f /tmp/environment.yaml && \
    conda clean -a -y


COPY torch-2.1.2+cu118-cp310-cp310-linux_x86_64.whl /tmp/torch-2.1.2+cu118-cp310-cp310-linux_x86_64.whl
COPY torchaudio-2.1.2+cu118-cp310-cp310-linux_x86_64.whl /tmp/torchaudio-2.1.2+cu118-cp310-cp310-linux_x86_64.whl
COPY torchvision-0.16.2+cu118-cp310-cp310-linux_x86_64.whl /tmp/torchvision-0.16.2+cu118-cp310-cp310-linux_x86_64.whl
COPY build_sql.py /tmp/build_sql.py
COPY build.sql /tmp/build.sql

# 9. 安装 pip 依赖
COPY requirements.txt /tmp/requirements.txt
RUN /bin/bash -c "source /opt/conda/etc/profile.d/conda.sh && \
    conda activate defect_env && \
    pip install PyQt-Fluent-Widgets -i https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip install -r /tmp/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip install /tmp/torch-2.1.2+cu118-cp310-cp310-linux_x86_64.whl && \
    pip install /tmp/torchaudio-2.1.2+cu118-cp310-cp310-linux_x86_64.whl && \
    pip install /tmp/torchvision-0.16.2+cu118-cp310-cp310-linux_x86_64.whl && \
    pip install ultralytics==8.3.91 --no-deps && \
    pip install ultralytics-thop==2.0.14 "
    
RUN rm /tmp/torch-2.1.2+cu118-cp310-cp310-linux_x86_64.whl && \
    rm /tmp/torchaudio-2.1.2+cu118-cp310-cp310-linux_x86_64.whl   && \
    rm /tmp/torchvision-0.16.2+cu118-cp310-cp310-linux_x86_64.whl



ENV CONDA_DEFAULT_ENV=defect_env
# ENV PATH="/opt/conda/envs/defect_env/bin:$PATH"
# SHELL ["conda", "run", "-n", "defect_env", "/bin/bash", "-c"]

# 6. 安装 TensorRT
COPY TensorRT-8.6.0.12.Linux.x86_64-gnu.cuda-11.8.tar.gz /tmp/
RUN tar -xzf /tmp/TensorRT-8.6.0.12.Linux.x86_64-gnu.cuda-11.8.tar.gz -C /opt && \
    rm /tmp/TensorRT-8.6.0.12.Linux.x86_64-gnu.cuda-11.8.tar.gz
ENV TENSORRT_DIR=/opt/TensorRT-8.6.0.12
ENV LD_LIBRARY_PATH=$TENSORRT_DIR/lib:$LD_LIBRARY_PATH
ENV CPATH=$TENSORRT_DIR/include:$CPATH
ENV LIBRARY_PATH=$TENSORRT_DIR/lib:$LIBRARY_PATH


# 8. 安装 wkhtmltox 及其依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    xfonts-75dpi \
    xfonts-base \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY wkhtmltox_0.12.6.1-2.jammy_amd64.deb /tmp/
RUN dpkg -i /tmp/wkhtmltox_0.12.6.1-2.jammy_amd64.deb && \
    rm /tmp/wkhtmltox_0.12.6.1-2.jammy_amd64.deb


RUN apt-get update && apt-get install -y xvfb
ENV DISPLAY=:0

# 8. 拷贝项目代码
COPY final /final
WORKDIR /final

RUN apt-get update && apt-get install nano

# 初始化 MySQL
RUN service mysql start && \
    mysql -u root -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '123456'; FLUSH PRIVILEGES;" && \
    service mysql stop

# 初始化 Conda
RUN /bin/bash -c "source /opt/conda/etc/profile.d/conda.sh"

# 将激活 Conda 环境的命令写入 .bashrc
RUN echo "source /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc
RUN echo "conda activate defect_env" >> ~/.bashrc

# 设置 QT 环境
ENV QT_QPA_PLATFORM_PLUGIN_PATH=/opt/conda/envs/defect_env/lib/python3.10/site-packages/PyQt5/Qt5/plugins/platforms/
RUN echo "export QT_QPA_PLATFORM_PLUGIN_PATH=/opt/conda/envs/defect_env/lib/python3.10/site-packages/PyQt5/Qt5/plugins/platforms/" >> ~/.bashrc

COPY Arial.ttf /root/.config/Ultralytics/Arial.ttf

# 设置启动命令
CMD ["bash", "-c", "service mysql start && \
source /opt/conda/etc/profile.d/conda.sh && \
conda activate defect_env && \
python /tmp/build_sql.py && \
/bin/bash "]

# 9. 容器启动后默认执行（根据项目实际修改）
# CMD [ "/usr/local/bin/start.sh", "conda", "run", "--no-capture-output", "-n", "defect_env", "python", "pyqt_1.py" ]

