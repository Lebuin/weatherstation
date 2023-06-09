FROM ubuntu:22.04

ARG ENV

ARG USERNAME=user
ARG USER_UID=1000
ARG USER_GID=1000

RUN groupadd --gid $USER_GID $USERNAME \
  && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
  && apt-get update \
  && apt-get install -y sudo \
  && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
  && chmod 0440 /etc/sudoers.d/$USERNAME \
  && rm -rf /var/lib/apt/lists/* /var/log/* /tmp/* /root/.cache
USER $USERNAME
WORKDIR /opt/data-receiver

RUN sudo apt-get update \
  && sudo apt-get install --no-install-recommends -y \
    python3 \
    python3-pip \
  && pip install -U pip \
  && sudo rm -rf /var/lib/apt/lists/* /var/log/* /tmp/* /root/.cache

COPY requirements.txt .
RUN pip install -r requirements.txt

CMD ["python3", "-m", "flask", "--app", "src.server", "run", "--host", "0.0.0.0", "--port", "5000", "--debug"]
