import argparse
import btle
import struct
import time

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
        peripheral.disconnect()

if __name__ == "__main__":
    p = argparse.ArgumentParser(description='Control a Nexturn Light Bulb (Yifang SH201)')
    p.add_argument('-a', '--address', type=str, help="Bulb MAC Addr(s)", action='append', dest="address", required=True)
    p.add_argument('-r', '--red', type=int, help="Integer Value for Red", action='store', dest="red")
    p.add_argument('-g', '--green', type=int, help="Integer Value for Green", action='store', dest="green")
    p.add_argument('-b', '--blue', type=int, help="Integer Value for Blue", action='store', dest="blue")
    p.add_argument('-i', '--intensity', type=int, help="Integer Value for Intensity", action='store', dest="intensity")
    p.add_argument('-p', '--preset', type=str, help="Color Preset From Config File", action="store", dest="preset")
    # p.add_argument('-c', '--config', type=str, help="Configuration File", action="store", dest="preset")
    arguments = p.parse_args()
    control(arguments)