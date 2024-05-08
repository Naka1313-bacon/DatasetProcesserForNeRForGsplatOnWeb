FROM  python:3.10.0
RUN pip install --upgrade pip
RUN pip install django rembg numpy pyinstaller
RUN apt-get update && apt-get install -y \
    git \
    cmake \
    build-essential \
    libboost-program-options-dev \
    libboost-filesystem-dev \
    libboost-graph-dev \
    libboost-regex-dev \
    libboost-system-dev \
    libboost-test-dev \
    libeigen3-dev \
    libsuitesparse-dev \
    libfreeimage-dev \
    libgoogle-glog-dev \
    libgflags-dev \
    libglew-dev \
    qtbase5-dev \
    libqt5opengl5-dev \
    libcgal-dev \
    libcgal-qt5-dev \
    libflann-dev \
    libmetis-dev \
    libatlas-base-dev \
    libsuitesparse-dev \
    libceres-dev \
    gettext \
    cron
RUN apt-get  install -y nano
# COLMAPのクローン、ビルド、インストール
RUN git clone https://github.com/colmap/colmap && \
    cd colmap && \ 
    mkdir build && \
    cd build && \
    cmake ../ && \
    make && \
    make install
# コンテナ起動時のコマンド
EXPOSE 8000
# cronジョブを設定（必要に応じて）
COPY crontab /etc/cron.d/my-cron-job
RUN chmod 0644 /etc/cron.d/my-cron-job

# cronデーモンをフォアグラウンドで実行
CMD ["cron", "-f"]
# サーバーを起動
CMD ["python", "manage.py", "runserver", "0:8000"]
CMD ["colmap"]