# LibNexturn

A command line interface to control a Yifang SH201 Bluetooth Lightbulb


## Dependencies

Depends on the [fantastic bluepy BTLE](https://github.com/IanHarvey/bluepy) library.

Bluetooth 4.0 (BTLE) support in hardware

Tested on python 2.7

## TODO

- Add support for color preset file

- Further investigation into other bluetooth "endpoints"

## EXAMPLES

All examples show the minimum arguments needed to work. 

### COLOR

`control.py rgb`

#### DEFAULT MODE

Set a particular color

`python control.py rgb color -a C4:ED:BA:56:00:00 --red 0 --green 102 --blue 202`

#### RANDOM

Sets a random color, currently mostly light colors / pastels

`python control.py rgb random -a C4:ED:BA:56:00:00`

### HSV

`control.py hue`

#### DEFAULT MODE

HSV Control mode

`python control.py hue color -a C4:ED:BA:56:00:00 --hue 0`

#### MINMAX

Pick a min Hue and a maximum hue, will select a color between the two values. If min > max, we go around the other direction

`python control.py hue minmax -a C4:ED:BA:56:00:00 --min 192 --max 15`

### CONFIGURATION AND NAME

TODO

## CHANGELOG

### 0.3 - 2014-07-04
- Refactored into reusable classes
- Exploration into name setting, name getting, no luck just yet.
- Better usage of `argparse`
- COL Bounce
- Updated Examples
- Sync modes for randoms, set all bulbs to the same random color, instead of individually `--sync0`

### 0.2 - 2014-06-23
- HSV Mode
- HSV MinMax
- COL Random

### 0.1 - 2014-06-21
- Initial Version with COL mode
  
