# 基础镜像
FROM python:3.10.14

COPY requirements.txt /

# 安装依赖
RUN pip install -i https://repo.huaweicloud.com/repository/pypi/simple -r requirements.txt

# 暴露端口
EXPOSE 8443

# 启动命令
CMD []