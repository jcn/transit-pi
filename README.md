# transit.py

A set of python scripts to fetch the next bus and subway arrival times for at a specific subway and bus stop for the NYC MTA. This was really built so we could easily know how much time we had to get to the bus or subway near our house, not for general trip planning.

Caveats:

* The concepts of "Uptown" and "Downtown" are hard-coded
* The stations, subway lines, and bus routes themselves are hard-coded into the app
* This code was only written to handle stations with only one subway or bus (since that's what we have); if you want to handle multiple lines, this code will definitely need to change
* This is absolute trash code, but I am hoping it helps someone else get up and running

## Hardware

* Raspberry Pi with internet access - I use a Zero W
* 128x64 OLED display - I am using a CH1116 (using the SH1106 driver) but this should also work with any SD1309, just update the display initialization

## Prerequisites

* Station IDs for subway and bus stops - these can be found in the stops.txt files found in the various GTFS downloads found at https://www.mta.info/developers or from the Bustime web interface at https://bustime.mta.info/
* Subway GTFS-Realtime URL - the URL for the specific line is at https://api.mta.info/#/subwayRealTimeFeeds 
* Bustime API Key - this needs to be requested at https://bt.mta.info/wiki/Developers/Index but will show up pretty quickly

## Setup

* apt-get install build-essential python3-dev python3-pip i2c-tools python3-lgpio swig liblgpio-dev libjpeg-dev
* You'll probably need a virtualenv set up for python (post Bookworm)
* pip install -r requirements.txt

## How it works

We put the following lines in the crontab:

```
* * * * * $HOME/transit/venv.sh fetch.py && $HOME/transit/venv.sh fetch_bus.py
@reboot $HOME/transit/venv.sh transit.py &
```

The venv.sh script changes into your directory, fires up the virtualenv, and then runs the python script.

The crontab above runs the fetch scripts every minute, and then ensures that the main transit.py script is run in the background after reboot. Is this robust? No. But whatever.
