#!/bin/bash

# To run this script, make sure gpio is installed
# git clone https://github.com/orangepi-xunlong/wiringOP.git
# cd wiringOP
# ./build clean
# sudo ./build
#
# Then, add this script to the startup scripts: add the line
#
# /home/orangepi/weatherstation/setup_pins.sh
#
# to /etc/rc.local

# KEEP THESE PIN NUMBERS IN SYNC WITH controller/config.py!
for pin in 2 4 6 8;
do
    gpio mode $pin in
    gpio mode $pin down
done
for pin in 3 5 7 9;
do
    gpio mode $pin out
done
