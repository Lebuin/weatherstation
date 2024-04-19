FROM ghcr.io/linuxserver/baseimage-alpine:3.18

RUN apk add --no-cache \
    python3 \
    py3-pip \
  && rm -rf /tmp/* /root/.cache

COPY orangepi-release /etc/orangepi-release

RUN apk add --no-cache --virtual .build-deps \
        git \
        g++ \
        linux-headers \
        make \
        python3-dev \
        py3-setuptools \
        swig \
    && git clone --recursive https://github.com/orangepi-xunlong/wiringOP-Python.git \
    && cd wiringOP-Python \
    && python3 generate-bindings.py > bindings.i \
    && python3 setup.py install \
    && cd .. \
    && rm -r wiringOP-Python \
    && apk del .build-deps \
    && rm -rf /tmp/* /root/.cache
