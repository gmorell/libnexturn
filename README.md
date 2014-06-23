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

### COLOR

`control.py color`

#### DEFAULT MODE

Set a particular color

`python control.py color -a C4:ED:BA:56:00:00 --red 0 --green 102 --blue 202`

#### RANDOM

Sets a random color, currently mostly light colors / pastels

`python control.py color -a C4:ED:BA:56:00:00 --mode random`

### HSV

`control.py hue`

#### DEFAULT MODE

HSV Control mode

`python control.py hue -a C4:ED:BA:56:00:00 --hue 0 --saturation 255 --value 255`

#### MINMAX

Pick a min Hue and a maximum hue, will select a color between the two values. If min > max, we go around the other direction

`python control.py hue -a C4:ED:BA:56:00:00 --mode minmax --min 192 --max 15`

## CHANGELOG

### 0.2
- HSV Mode
- HSV MinMax
- COL Random

### 0.1
- Initial Version with COL mode
  
