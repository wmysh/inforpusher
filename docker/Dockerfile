FROM python:3.8-alpine3.12
MAINTAINER wuyehow <wyhadter@outlook.com>

WORKDIR /inforpusher

RUN set -ex \
    && apk add --no-cache tzdata moreutils git gcc g++ py-pip libffi-dev \
    && ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && echo "Asia/Shanghai" > /etc/timezone

RUN set -ex \
    && git clone https://github.com/WuYehow/inforpusher.git /inforpusher \
    && cd /inforpusher \
    && mkdir logs

RUN set -ex \
    && pip install -r requirements.txt

ENTRYPOINT ["python","main.py"]