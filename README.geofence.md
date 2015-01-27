# LIbNexturn GeoFencing

pings a given host and if its there changes the color of one or more bulbs

## Dependencies

A working libnexturn

## usage

to your crontab, add a line like so:

`python geofence.py -m C4:ED:BA:56:00:00 -i 192.168.1.101 -b 0 -c 128`