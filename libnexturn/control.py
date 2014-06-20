import argparse
import btle
import struct

def control(arguments):
    # temporary
    print arguments
    # TODO LIST
    # grab bulbs from args
    # iterate
    # connect
    # apply
    # - done

    # something like

    # for i in arguments.address:
    #     peripheral = btle.Peripheral(i)
    #     peripheral.discoverServices()
    #     colorcontrol = peripheral.services.values()[3]
    #     x = colorcontrol.getCharacteristics()
    #
    #     if arguments.red:
    #         ss = struct.pack('h',arguments.red)[0]
    #         x[0].write(ss)
    #
    #     if arguments.green:
    #         ss = struct.pack('h',arguments.green)[0]
    #         x[1].write(ss)
    #
    #     if arguments.blue:
    #         ss = struct.pack('h',arguments.blue)[0]
    #         x[2].write(ss)
    #
    #     if arguments.intensity:
    #         ss = struct.pack('h',arguments.intensity)[0]
    #         x[3].write(ss)

    #     disconnect()

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