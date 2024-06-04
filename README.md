# Orange PI setup

* Download the most recent [Ubuntu image](https://drive.google.com/drive/folders/1KzyzyByev-fpZat7yvgYz1omOqFFqt1k)
* Flash it to an SD card using [balenaEtcher](https://etcher.balena.io/#download-etcher)
* Set up the network to connect to on first boot:
* Set up the Wifi network to connect to on first boot: Navigate to the /boot folder of the SD card, copy the file `orangepi_first_run.txt.template` to `orangepi_first_run.txt`, and set the following options for ethernet (assuming you will install the OrangePi directly in the greenhouse, otherwise adjust the ip address accordingly):

```
FR_net_change_defaults=1
FR_net_ethernet_enabled=1
FR_net_wifi_enabled=0
FR_net_use_static=1
FR_net_static_ip='10.9.10.5'
FR_net_static_mask='255.255.255.0'
FR_net_static_gateway='10.9.10.254'
```

Or the following options for Wifi:

```
FR_net_change_defaults=1
FR_net_wifi_enabled=1
FR_net_wifi_ssid=<ssid>
FR_net_wifi_key=<password>
FR_net_wifi_countrycode='BE'
```

* Put the SD card into the OPI and boot it.
* SSH into the OPI with username orangepi and password orangepi.
* Set the timezone `sudo timedatectl set-timezone Europe/Brussels`.
* Set a new password: `passwd`.
* Switch to a faster apt mirror: `sudo sed -i.bak -e 's/mirrors.tuna.tsinghua.edu.cn/mirrors.ocf.berkeley.edu/g' /etc/apt/sources.list`.
* Install [WiringOP](https://github.com/orangepi-xunlong/wiringOP).
* Install [Docker](https://docs.docker.com/engine/install/ubuntu/).
* Clone the repo: `git clone https://github.com/Lebuin/weatherstation.git`.
* Add the line `/home/orangepi/weatherstation/setup_pins.sh` to /etc/rc.local.
* Reboot.
* Run `docker compose up -d` in the weatherstation folder.


# Development

There are 2 parts to this application:

* `data-receiver` runs a webserver. Every minute the Froggit weather station posts a weather report to this server, which is then translated into a more sensible format and posted on a MQTT topic.
* `controller` subscribes both to this MQTT topic, and to the status of the 4 physical buttons on the weather station case. Based on these inputs, it controls the 2 motors of the greenhouse.

While developing, the following may come in handy:

* By setting `config.MODE = motor_io.Mode.KEYBOARD`, you can send inputs to `controller` with the keyboard keys a/z/k/m. This only works when the controller is running locally, not inside docker.
* By setting `config.MODE = motor_io.Mode.MQTT`, you can send inputs to `controller` by sending mqtt messages. This also works when running inside docker. For example, to signal that the north/open button is pressed, you can run `mosquitto_pub -u debug -P debug -t weatherstation/roof/north/open -m 1`. Note that you have to manually depress the button by sending `-t weatherstation/roof/north/open -m 1` before you can "press" it a second time.
* You can send fake weather reports to `data-receiver`, for example: `curl "localhost:5000/report?ID=biotope-serre&PASSWORD=biotope9000&tempf=77.2&humidity=62&dewptf=63.1&windchillf=77.2&winddir=24&windspeedmph=0.00&windgustmph=0.00&rainin=0.000&dailyrainin=0.000&weeklyrainin=0.000&monthlyrainin=0.000&yearlyrainin=-9999&totalrainin=0.000&solarradiation=18.05&UV=0&indoortempf=76.5&indoorhumidity=61&absbaromin=29.867&baromin=29.923&lowbatt=1&dateutc=now&softwaretype=EasyWeatherPro_V5.1.1&action=updateraw&realtime=1&rtfreq=5"`
