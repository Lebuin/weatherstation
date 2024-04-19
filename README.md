# Orange PI setup

* Download the most recent [Ubuntu image](https://drive.google.com/drive/folders/1KzyzyByev-fpZat7yvgYz1omOqFFqt1k)
* Flash it to an SD card using [balenaEtcher](https://etcher.balena.io/#download-etcher)
* Set up the Wifi network to connect to on first boot: Navigate to the /boot folder of the SD card, copy the file `orangepi_first_run.txt.template` to `orangepi_first_run.txt`, and set the following options:

```
FR_net_change_defaults=1
FR_net_wifi_enabled=1
FR_net_wifi_ssid=<ssid>
FR_net_wifi_key=<password>
FR_net_wifi_countrycode='BE'
```

* SSH into the OPI with username orangepi and password orangepi.
* Install [Docker](https://docs.docker.com/engine/install/ubuntu/)
* Clone the repo: `git clone https://github.com/Lebuin/weatherstation.git`
