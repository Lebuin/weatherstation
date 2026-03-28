# Orange PI setup

## Installation

* Download the most recent [OrangePi Ubuntu image](https://drive.google.com/drive/folders/1KzyzyByev-fpZat7yvgYz1omOqFFqt1k)
* Flash it to an SD card using [balenaEtcher](https://etcher.balena.io/#download-etcher)
* Set up the Wifi network to connect to on first boot: Navigate to the /boot folder of the SD card (this folder is owned by root, so you need root access), copy the file `orangepi_first_run.txt.template` to `orangepi_first_run.txt`, and add the following lines to the end of the file:

```
FR_net_change_defaults=1
FR_net_wifi_enabled=1
FR_net_wifi_ssid='Biotope gast'
FR_net_wifi_key='biotope9000'
FR_net_wifi_countrycode='BE'
```

* Before booting the OPI, find a list of devices that are currently connected to the Biotope network: connect to the Biotope VPN (it's not enough if you are connected to the network yourself), run `sudo nmap -sn 10.9.10.0/24` and note down the results
* Put the SD card into the OPI and boot it.

## Connecting for the first time and initial configuration

* Find the IP address of the OPI: connect to Biotope VPN, run `sudo nmap -sn 10.9.10.0/24` again and find new IP addresses. Try to connect to them with `ssh orangepi@10.9.10.x` (password orangepi).
* Set the timezone `sudo timedatectl set-timezone Europe/Brussels`.
* Set a new password: `passwd` (and write it down in the manual).
* Switch to a faster apt mirror:

```
sudo sed -i.bak -e 's/mirrors.tuna.tsinghua.edu.cn/mirrors.ocf.berkeley.edu/g' /etc/apt/sources.list
sudo apt update
```

## Set up reverse tunnels through lenders.dev

* In the OPI, run `ssh-keygen`
* Copy the contents of `.ssh/id_rsa.pub` to `lenders.dev/authorized_keys`
* Run `ssh seppe@lenders.dev` and confirm adding lenders.dev to the list of known hosts. This should log in without asking for a password.
* Create `/etc/systemd/system/autossh.service` with the following content:

```
[Unit]
Description=Open tunnels to lenders.dev

[Service]
User=orangepi
WorkingDirectory=/home/orangepi
ExecStart=autossh -TN -o "ServerAliveInterval 10" -o "ServerAliveCountMax 3" -o "ExitOnForwardFailure=yes" -R 0.0.0.0:8023:localhost:22 -R 0.0.0.0:5000:localhost:5000 seppe@lenders.dev
Restart=always
RestartSec=10s

[Install]
WantedBy=multi-user.target
```

* Run:

```
sudo apt install -y autossh
sudo systemctl enable --now autossh
```

* On lenders.dev, make sure the following lines are added to `/etc/ssh/sshd_config` (NOT
  `/etc/ssh/ssh_config`) and run `sudo systemctl restart ssh`:

```
GatewayPorts yes
ClientAliveInterval 10
ClientAliveCountMax 3
```

* Now you should be able to do `ssh orangepi@lenders.dev -p 8023` from your local machine

## Install the controller app

* Install [WiringOP](https://github.com/orangepi-xunlong/wiringOP).
* Install [Docker](https://docs.docker.com/engine/install/ubuntu/) (make sure to follow the post-installation steps).
* Clone the repo: `git clone https://github.com/Lebuin/weatherstation.git`.
* Add the line `/home/orangepi/weatherstation/setup_pins.sh` to `/etc/rc.local` (before the line `exit 0`).
* Reboot.
* Run `docker compose up -d` in the weatherstation folder.


# Development

There are 2 parts to this application:

* `data-receiver` runs a webserver on port 5000. Every minute the Froggit weather station posts a weather report to this server (`/report` route), which is then translated into a more sensible format and posted on a MQTT topic. In addition, the Bijgaardehub queries the `/state` route to get info about the current state of the system.
* `controller` subscribes both to this MQTT topic, and to the status of the 4 physical buttons on the weather station case. Based on these inputs, it controls the 2 motors of the greenhouse.

While developing, the following may come in handy:

* By setting `config.MODE = motor_io.Mode.KEYBOARD`, you can send inputs to `controller` with the keyboard keys a/z/k/m. This only works when the controller is running locally, not inside docker.
* By setting `config.MODE = motor_io.Mode.MQTT`, you can send inputs to `controller` by sending mqtt messages. This also works when running inside docker. For example, to signal that the north/open button is pressed, you can run `mosquitto_pub -u debug -P debug -t weatherstation/roof/north/open -m 1`. Note that you have to manually depress the button by sending `-t weatherstation/roof/north/open -m 1` before you can "press" it a second time.
* You can send fake weather reports to `data-receiver`, for example: `curl "localhost:5000/report?ID=biotope-serre&PASSWORD=biotope9000&tempf=77.2&humidity=62&dewptf=63.1&windchillf=77.2&winddir=24&windspeedmph=0.00&windgustmph=0.00&rainin=0.000&dailyrainin=0.000&weeklyrainin=0.000&monthlyrainin=0.000&yearlyrainin=-9999&totalrainin=0.000&solarradiation=18.05&UV=0&indoortempf=76.5&indoorhumidity=61&absbaromin=29.867&baromin=29.923&lowbatt=1&dateutc=now&softwaretype=EasyWeatherPro_V5.1.1&action=updateraw&realtime=1&rtfreq=5"`
