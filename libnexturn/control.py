import argparse
import btle
import colorsys
import datetime
import random
import re
import struct
import time

modes_color = ['color', 'random']
modes_hue = ['color', 'minmax']

HELP_STRING_ADDR_P = "Bulb MAC Addr(s)"
HELP_STRING_ADDR = "Bulb MAC Addr"

### Argparse Helpers

## Types
def MacAddrType(v):
    try:
        return re.match(r'([0-9A-F]{2}[:-]){5}([0-9A-F]{2})', v).group(0)
    except:
        raise argparse.ArgumentTypeError("Given value '%s' is not a valid mac address"%(v,))

def IPV4AddrType(v):
    try:
        return re.match( r'[0-9]+(?:\.[0-9]+){3}', v).group(0)
    except:
        raise argparse.ArgumentTypeError("Given value '%s' is not a valid ipv4 address"%(v,))
def RGBType(v):
    # check that we're a comma seperated list
    try:
        val1 = re.match(r'[0-9]+(,[0-9]+){2}', v).group(0)
    except:
        raise argparse.ArgumentTypeError("Given value '%s' is not a valid RGB Tuple (r,g,b) "%(v,))

    print val1
    val2 = [int(i) for i in val1.split(',')]
    for i in val2:
        if i < 0 or i > 255:
            raise argparse.ArgumentTypeError("Please make sure all RGB values in '%s' are between 0 and 255"%(v,))

    return val2

## Actions
def required_length():
    class RequiredLength(argparse.Action):
        def __call__(self, parser, args, values, option_string=None):
            if len(values) < 2:
                msg='Need at least 2 RGB Values to bounce between'
                raise argparse.ArgumentTypeError(msg)
            setattr(args, self.dest, values)
    return RequiredLength


class NexturnConnectionController(object):

    def connect(self, addr):
        while True:
            try:
                peripheral = btle.Peripheral(addr)

            except IOError:
                # raise
                #TODO add a cannot find exception here, in addition to failing to connect the first time
                print 'failed to find s%s , trying again in a moment' % addr
                time.sleep(5)
                return None
            except:
                print 'failed to connect to %s , trying again in a moment' % addr
                time.sleep(5)
                # raise
                # return None
            else:
                #the rest of the code
                break
        return peripheral


class NexturnRGBController(NexturnConnectionController):
    def __init__(self, args):
        try:
            cmd = self.__getattribute__(args.command_rgb)
        except:
            raise Exception("Command Not Implemented")

        self.args = args
        self.argsdict = args.__dict__  # hacky
        if self.argsdict.get("sync",False):
            self.sync = True
        else:
            self.sync = False
        # trying out a connection pool.
        self.peripherals = filter(None, [self.connect(a) for a in self.args.address])
        cmd()
        for p in self.peripherals:
            p.disconnect()

    def step_to(self, pres, dest, stepsize=4):
        """ Steps Somewhere """
        if abs(pres-dest) > stepsize:
            if pres > dest:
                pres -= stepsize
            elif pres < dest:
                pres += stepsize
            else:
                pass
        else:
            pres = dest
        return pres

    def rgbstepTo(self, current=[0, 0, 0],desired=[0, 0, 0]):
        print current, desired
        x = [self.step_to(c, d, stepsize=self.args.step) for c, d in zip(current, desired)]
        return x


    def _get_rand_rgb(self):
        """
        Returns a random RGB
        """
        red = random.randint(0, 255)
        green = random.randint(0, 255)
        blue = random.randint(0, 255)

        return red, green, blue

    def _write_rgb(self, r, g, b, peripheral):
        # print r,g,b

        # return
        # if anyone can find a better way to do this, it would be swell
        rc = struct.pack('h', r)[0]
        gc = struct.pack('h', g)[0]
        bc = struct.pack('h', b)[0]

        # get services
        peripheral.discoverServices()
        colorcontrol = peripheral.services.values()[2]

        # get the values
        x = colorcontrol.getCharacteristics()

        # write
        x[0].write(rc)
        x[1].write(gc)
        x[2].write(bc)



    def rgb(self, r, g, b, p):
        self._write_rgb(r, g, b, p)

    def rgb_all(self, r, g, b):
        """
         writes values to all available peripherals
        """
        for p in self.peripherals:
            self._write_rgb(r, g, b, p)

    def color(self):
        self.rgb_all(self.args.red, self.args.green, self.args.blue)

    def random(self):
        """
        Pick a random color, switch to it.
        """
        if self.sync:  # all bulbs the same
            red, green, blue = self._get_rand_rgb()

            for p in self.peripherals:
                self.rgb(red, green, blue, p)

        else: # all different
            for p in self.peripherals:
                red, green, blue = self._get_rand_rgb()

                self.rgb(red, green, blue, p)

    # def random_for_duration(self):
    #     """
    #     Bounces between random colors for a given duration
    #     """
    #     pass

    def bounce(self):
        """
        Bounces between set random colors for a given duration
        """
        now = datetime.datetime.now()
        end = now + datetime.timedelta(seconds=self.args.duration)
        sleepperiod = float(self.args.wait)

        current = self.args.colors[0]
        print "INITIAL", current
        self.rgb_all(*current)
        while datetime.datetime.now() < end:
            for c in self.args.colors:
                while current != c:
                    current = self.rgbstepTo(current, c)
                    print "STEPPING TO %s" % current
                    self.rgb_all(*current)
                    print "SLEEPING"
                    time.sleep(sleepperiod)


class NexturnHSVController(NexturnRGBController):
    def __init__(self,args):
        try:
            cmd = self.__getattribute__(args.command_hue)
        except:
            raise Exception("Command Not Implemented")

        self.args = args
        self.argsdict = args.__dict__ #hacky
        if self.argsdict.get("sync",False):
            self.sync = True
        else:
            self.sync = False
        # trying out a connection pool.
        self.peripherals = filter(None, [self.connect(a) for a in self.args.address])
        cmd()
        for p in self.peripherals:
            p.disconnect()

    # various helpers and utilities
    def _write_hsv(self, h, s, v, p):
        r, g, b = self._hsv_to_rgb(h, s, v)
        self._write_rgb(r, g, b, p)

    def _write_hsv_all(self, h, s, v):
        r, g, b = self._hsv_to_rgb(h, s, v)
        self.rgb_all(r, g, b)

    def _sys_255_to_1(self, values):
        return [i/255.0 for i in values]

    def _sys_1_to_255(self, values):
        return [i*255 for i in values]

    def _hsv_to_rgb(self, h, s, v):
        h_, s_, v_ = self._sys_255_to_1([h, s, v])
        r_, g_, b_ = colorsys.hsv_to_rgb(h_, s_, v_)
        r, g, b = self._sys_1_to_255([r_, g_, b_])
        return r, g, b

    def _get_a_minmax(self, mini, maxi):
        if mini <= maxi:
            h_ = random.randint(mini, maxi)
        else:  # we do a clever wrap-around
            min_a = mini
            max_a = 255

            min_b = 0
            max_b = maxi

            ch = random.choice(['a', 'b'])
            if ch == 'a':
                h_ = random.randint(min_a, max_a)
            elif ch == 'b':
                h_ = random.randint(min_b, max_b)

        return h_

    def minmax(self):
        mini = self.args.min
        maxi = self.args.max
        sat = self.args.saturation
        val = self.args.value

        if self.args.sync:
            hue = self._get_a_minmax(mini, maxi)
            self._write_hsv_all(hue, sat, val)

        else:
            for p in self.peripherals:
                hue = self._get_a_minmax(mini, maxi)
                self._write_hsv(hue, sat, val, p)


    def color(self):
        self._write_hsv_all(self.args.hue, self.args.saturation, self.args.value)

    def random(self):
        sat = self.args.saturation
        val = self.args.value
        if self.args.sync:
            hue = random.randint(0,255)
            self._write_hsv_all(hue, sat, val)

        else:
            for p in self.peripherals:
                hue = random.randint(0,255)
                self._write_hsv(hue, sat, val, p)

class NexturnNameController(NexturnConnectionController): # UNTESTED
    def __init__(self, args):
        bulb = self.connect(args.address)
        if args.command_conf == "name_set":
            self.name_set()
            # write to bulb, see peripheral.services.values()[3] to figure out where to write
            # confirm and return name
        elif args.command_conf == "name_get":
            self.name_get()
            # read bulb, return name

    def name_get(self):
        print "READING_NOT_IMPL, HAVEN'T FOUND THE CHARACTERISTIC TO WRITE TO, MAKE A PR IF YOU DID"

    def name_set(self):
        print "WRITING_NOT_IMPL, HAVEN'T FOUND THE CHARACTERISTIC TO WRITE TO, MAKE A PR IF YOU DID"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Control a Nexturn Light Bulb (Yifang SH201)')
    subparsers = parser.add_subparsers()

    # color parse
    parse_color = subparsers.add_parser('rgb')
    pc = parse_color.add_subparsers(dest="command_rgb")

    parse_color = pc.add_parser('color')
    parse_color.add_argument(
        '-a', '--address', type=MacAddrType, help=HELP_STRING_ADDR_P, action='append', dest="address", required=True
    )
    parse_color.add_argument(
        '-r', '--red', type=int, help="Integer Value for Red", action='store', dest="red", required=True
    )
    parse_color.add_argument(
        '-g', '--green', type=int, help="Integer Value for Green", action='store', dest="green", required=True
    )
    parse_color.add_argument(
        '-b', '--blue', type=int, help="Integer Value for Blue", action='store', dest="blue", required=True
    )
    parse_color.add_argument(
        '-i', '--intensity', type=int, help="Integer Value for Intensity", action='store', dest="intensity"
    )


    parse_rand = pc.add_parser('random')
    parse_rand.add_argument(
        '-a', '--address', type=MacAddrType, help=HELP_STRING_ADDR_P, action='append', dest="address", required=True
    )
    parse_rand.add_argument(
        '-y', '--sync', help="All Bulbs Same Color", action='store_true', default=False, dest="sync"
    )

    parse_rand = pc.add_parser('bounce') # this one is still shot.
    parse_rand.add_argument(
        '-a', '--address', type=MacAddrType, help=HELP_STRING_ADDR_P, action='append', dest="address", required=True
    )
    parse_rand.add_argument(
        '-c', '--colors', type=RGBType, help="Bulb Color String (R,G,B)", action='append', dest="colors", required=True
    )  # add required_length() from above later to action instead of append
    parse_rand.add_argument(
        '-d', '--duration', type=int, help="Program Duration in seconds", action='store', dest="duration", default=600
    )
    parse_rand.add_argument(
        '-w', '--waitperiod', type=float, help="Time to wait between steps", action='store', dest="wait", default=20
    )
    parse_rand.add_argument(
        '-s', '--step', type=int, help="step size", action='store', dest="step", default=30
    )

    # hue parse
    parse_hue = subparsers.add_parser('hue')
    ph = parse_hue.add_subparsers(dest="command_hue")

    ph_color = ph.add_parser('color')
    ph_color.add_argument(
        '-a', '--address', type=MacAddrType, help=HELP_STRING_ADDR_P, action='append', dest="address", required=True
    )
    ph_color.add_argument(
        '-i', '--hue', type=int, help="Integer Value for Hue", action='store', dest="hue",required=True
    )
    ph_color.add_argument(
        '-s', '--saturation', type=int, help="Integer Value for Saturation", action='store', dest="saturation", default=255
    )
    ph_color.add_argument(
        '-v', '--value', type=int, help="Integer Value for Value", action='store', dest="value", default=255
    )

    ph_minmax = ph.add_parser('minmax')
    ph_minmax.add_argument(
        '-a', '--address', type=MacAddrType, help=HELP_STRING_ADDR_P, action='append', dest="address", required=True
    )
    ph_minmax.add_argument(
        '-m', '--min', type=int, help="Minimum hue value for minmax mode",action='store', dest="min",required=True
    )
    ph_minmax.add_argument(
        '-n', '--max', type=int, help="Maximum hue value for minmax mode", action='store', dest="max",required=True
    )
    ph_minmax.add_argument(
        '-s', '--saturation', type=int, help="Int Value for Saturation", action='store', dest="saturation", default=255
    )
    ph_minmax.add_argument(
        '-v', '--value', type=int, help="Int Value for Value", action='store', dest="value", default=255
    )
    ph_minmax.add_argument(
        '-y', '--sync', help="All Bulbs Same Color", action='store_true', default=False, dest="sync"
    )

    ph_random = ph.add_parser('random')
    ph_random.add_argument(
        '-a', '--address', type=MacAddrType, help=HELP_STRING_ADDR_P, action='append', dest="address", required=True
    )
    ph_random.add_argument(
        '-s', '--saturation', type=int, help="Int Value for Saturation", action='store', dest="saturation", default=255
    )
    ph_random.add_argument(
        '-v', '--value', type=int, help="Int Value for Value", action='store', dest="value", default=255
    )
    ph_random.add_argument(
        '-y', '--sync', help="All Bulbs Same Color", action='store_true', default=False, dest="sync"
    )

    ### Management Parsers
    parse_conf = subparsers.add_parser("config")
    pc_name = parse_conf.add_subparsers(dest="command_conf")

    ## get a bulb's name
    pc_name_get = pc_name.add_parser('name_get')
    pc_name_get.add_argument(
        '-a', '--address', type=MacAddrType, help=HELP_STRING_ADDR, action='store', dest="address", required=True
    )

    ## set a bulb's name
    pc_name_set = pc_name.add_parser('name_set')
    pc_name_set.add_argument(
        '-a', '--address', type=MacAddrType, help=HELP_STRING_ADDR, action='store', dest="address", required=True
    )
    pc_name_set.add_argument(
        '-n', '--name', type=str, help="Bulb Name String", action='store', dest="name", required=True
    )

    # planned
    # p.add_argument('-p', '--preset', type=str, help="Color Preset From Conf File", action="store", dest="preset")
    # p.add_argument('-c', '--config', type=str, help="Configuration File", action="store", dest="preset")

    # couldn't think of a better way to get these values
    arguments = parser.parse_args()
    argumentsdict = arguments.__dict__
    print arguments
    if argumentsdict.get('command_conf',None) in ['name_get', 'name_set']:
        NexturnNameController(arguments)

    elif argumentsdict.get('command_hue', None) in ['color', 'minmax', 'random']:
        NexturnHSVController(arguments)

    elif argumentsdict.get('command_rgb', None) in ['color', 'random', 'bounce']:
        NexturnRGBController(arguments)

    else:
        raise Exception("Bad Args, No Class")
    # control(arguments)




## Search Pattern
# import btle, time
# p = btle.Peripheral("C4:ED:BA:56:8D:05")
# p.discoverServices()
# key = 1
# for x in p.services.values():
#     print "KEY", key
#     y = x.getCharacteristics()
#     for z in y:
#         try:
#             z.read()
#         except:
#             print "failed to read", z
#         time.sleep(10)
#
#     key += 1
#
# p.disconnect()