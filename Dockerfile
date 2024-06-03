# app/Dockerfile

FROM python:3.11-slim

# RUN apt-get update && apt-get install -y \
# 	tzdata \
# #    build-essential \
# #    software-properties-common \
#     git \
# 	pip \
#     && rm -rf /var/lib/apt/lists/*

ENV TZ=Asia/Tokyo
ARG PROXY=
ARG HTTP_PROXY=$PROXY
ARG HTTPS_PROXY=$PROXY

ENV http_proxy=$PROXY
ENV https_proxy=$PROXY

WORKDIR /app

COPY ./base/requirements_01.txt ./
RUN pip install --no-cache-dir \
	-r requirements_01.txt

# RUN apt-get update && apt-get install antiword

# 資材ファイルのコピー
COPY ./base /app/base
COPY ./data /app/data

# baseディレクトリを作業ディレクトリに設定
WORKDIR /app/base

# アプリケーションの実行
CMD ["/bin/bash", "-c", "ls /app/base"]
# 実際必要なのはこっち
# CMD ["python", "test_base_01.py"]
CMD ["python", "base_simple.py"]
