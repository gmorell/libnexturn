import argparse
import btle
import colorsys
import random
import struct
import time

modes_color = ['color','random']
modes_hue = ['color','minmax']

def control(arguments):
    # temporary
    # print arguments


    for i in arguments.address:
        # if at first we don't succeed try until we die.
        # this is a bit of a hack, but the bulb is finicky.
        while True:
            try:
                peripheral = btle.Peripheral(i)

            except:
                print 'failed to connect to %s , trying again in a moment' % i
                time.sleep(3)
                continue

            else:
                #the rest of the code
                break

        # after connecting we get the service list
        peripheral.discoverServices()

        # get the color control service
        colorcontrol = peripheral.services.values()[2]

        # get the values
        x = colorcontrol.getCharacteristics()

        # go into our macromodes
        if arguments.macromode == "color":
            # do things
            if arguments.mode[0] == "color":

                # do that thing
                if arguments.red or arguments.red == 0:
                    ss = struct.pack('h',arguments.red)[0]
                    x[0].write(ss)

                if arguments.green or arguments.green == 0:
                    ss = struct.pack('h',arguments.green)[0]
                    x[1].write(ss)

                if arguments.blue or arguments.blue == 0:
                    ss = struct.pack('h',arguments.blue)[0]
                    x[2].write(ss)

                if arguments.intensity or arguments.intensity == 0:
                    ss = struct.pack('h',arguments.intensity)[0]
                    x[3].write(ss)

                # disconnect, else it gets angry

            if arguments.mode[0] == "random":
                # print "RANDOM"
                red_choice = random.randint(0,255)
                blue_choice = random.randint(0,255)
                green_choice = random.randint(0,255)

                rc = struct.pack('h',red_choice)[0]
                x[0].write(rc)

                gc = struct.pack('h',green_choice)[0]
                x[1].write(gc)

                bc = struct.pack('h',blue_choice)[0]
                x[2].write(bc)

        elif arguments.macromode == "hue":
            if arguments.mode[0] == "minmax":
                if arguments.min < arguments.max:
                    min = arguments.min
                    max = arguments.max
                    h_ = random.randint(min,max) / 255.0

                else: # we do a clever wrap-around
                    min_a = arguments.min
                    max_a = 255

                    min_b = 0
                    max_b = arguments.max

                    ch = random.choice(['a', 'b'])
                    if ch == 'a':
                        h_ = random.randint(min_a, max_a) / 255.0
                    elif ch == 'b':
                        h_ = random.randint(min_b, max_b) / 255.0

                s_ = arguments.saturation / 255.0
                v_ = arguments.value / 255.0
                r,g,b = colorsys.hsv_to_rgb(h_, s_, v_)
                red_choice = r * 255
                blue_choice = b * 255
                green_choice = g * 255



            elif arguments.mode[0] == "color":
                h_ = arguments.hue / 255.0
                s_ = arguments.saturation / 255.0
                v_ = arguments.value / 255.0
                red_choice,green_choice,blue_choice = colorsys.hsv_to_rgb(h_, s_, v_)
                red_choice = red_choice * 255
                blue_choice = blue_choice * 255
                green_choice = green_choice * 255

            rc = struct.pack('h',red_choice)[0]
            x[0].write(rc)

            gc = struct.pack('h',green_choice)[0]
            x[1].write(gc)

            bc = struct.pack('h',blue_choice)[0]
            x[2].write(bc)
        peripheral.disconnect()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Control a Nexturn Light Bulb (Yifang SH201)')
    subparsers = parser.add_subparsers()

    parse_color = subparsers.add_parser('color')
    parse_color.set_defaults(macromode="color")

    parse_color.add_argument('-a', '--address', type=str, help="Bulb MAC Addr(s)", action='append', dest="address", required=True)
    parse_color.add_argument('-r', '--red', type=int, help="Integer Value for Red", action='store', dest="red")
    parse_color.add_argument('-g', '--green', type=int, help="Integer Value for Green", action='store', dest="green")
    parse_color.add_argument('-b', '--blue', type=int, help="Integer Value for Blue", action='store', dest="blue")
    parse_color.add_argument('-i', '--intensity', type=int, help="Integer Value for Intensity", action='store', dest="intensity")
    parse_color.add_argument('-m', '--mode', nargs=1, action="store", choices=modes_color, default=['color'])

    parse_hue = subparsers.add_parser('hue')
    parse_hue.set_defaults(macromode="hue")

    parse_hue.add_argument('-a', '--address', type=str, help="Bulb MAC Addr(s)", action='append', dest="address", required=True)
    parse_hue.add_argument('-i', '--hue', type=int, help="Integer Value for Hue", action='store', dest="hue")
    parse_hue.add_argument('-s', '--saturation', type=int, help="Integer Value for Saturation", action='store', dest="saturation", default=255)
    parse_hue.add_argument('-v', '--value', type=int, help="Integer Value for Value", action='store', dest="value", default=255)
    parse_hue.add_argument('-n', '--min', type=int, help="Minimum hue value for minmax mode",action='store', dest="min")
    parse_hue.add_argument('-o', '--max', type=int, help="Maxiumum hue value for minmax mode", action='store', dest="max")
    parse_hue.add_argument('-m', '--mode', nargs=1, action="store", choices=modes_hue, default=['color'])

    # parser.add_argument('-p', '--preset', type=str, help="Color Preset From Config File", action="store", dest="preset")
    # parser.add_argument('-m', '--mode', nargs=1, action="store", choices=modes, default=['color'])
    # p.add_argument('-c', '--config', type=str, help="Configuration File", action="store", dest="preset")
    arguments = parser.parse_args()
    # print arguments
    control(arguments)