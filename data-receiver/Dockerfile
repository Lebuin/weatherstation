FROM ghcr.io/linuxserver/baseimage-alpine:3.18

RUN apk add --no-cache \
    python3 \
    py3-pip \
  && rm -rf /tmp/* /root/.cache

COPY root /

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src /app
