# Useful links

WiringOP library: https://github.com/orangepi-xunlong/wiringOP-Python
Docker GPIO: https://stackoverflow.com/questions/30059784/docker-access-to-raspberry-pi-gpio-pins
APT Mirrors: https://askubuntu.com/a/1477194

# Install GPIO stuff

```
sudo apt update
sudo apt install git swig python3-dev python3-setuptools
git clone --recursive https://github.com/orangepi-xunlong/wiringOP-Python.git
cd wiringOP-Python
python3 generate-bindings.py > bindings.i
sudo python3 setup.py install

sudo python3

import wiringpi
wiringpi.wiringPiSetup()
wiringpi.pinMode(1, 1)  # OUTPUT
wiringpi.digitalWrite(1, 1)
wiringpi.pinMode(1, 0)  # INPUT
wiringpi.digitalRead(1)
```

# Access GPIO in Docker

Ubuntu:
```
docker run -ti --privileged ubuntu bash
# In case ports.ubuntu.com is slow:
sed -ie 's|ports.ubuntu.com|in.mirror.coganng.com|' /etc/apt/sources.list
apt update && apt install -y git swig python3-dev python3-setuptools build-essential
git clone --recursive https://github.com/orangepi-xunlong/wiringOP-Python.git && cd wiringOP-Python
python3 generate-bindings.py > bindings.i && python3 setup.py install
```

Alpine:
```
docker run -ti --privileged ghcr.io/linuxserver/baseimage-alpine:3.18 bash
apk add --no-cache git swig python3-dev py3-setuptools g++ make linux-headers
git clone --recursive https://github.com/orangepi-xunlong/wiringOP-Python.git && cd wiringOP-Python
python3 generate-bindings.py > bindings.i && python3 setup.py install
```
