FROM ghcr.io/linuxserver/baseimage-alpine:3.18

RUN apk install --no-cache python3

COPY orangepi-release /etc/orangepi-release

RUN buildDeps="swig python3-dev py3-setuptools g++ make linux-headers" \
    && apk add --no-cache $buildDeps \
    && git clone --recursive https://github.com/orangepi-xunlong/wiringOP-Python.git \
    && cd wiringOP-Python \
    && python3 generate-bindings.py > bindings.i \
    && python3 setup.py install \
    && cd .. \
    && rm -r wiringOP-Python \
    && rm -rf /tmp/* /root/.cache
