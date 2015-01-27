import argparse
from libnexturn.control import NexturnHSVController as NHSVC
from libnexturn.control import MacAddrType, IPV4AddrType
import os


def main(ipaddress, here=0, there=128, macaddress=[]):
    response = os.system("ping -c 1 " + ipaddress)
    if response == 0: # its here
        color = here
    else:
        color = there
        
    kwargs = {
        "address":macaddress,
        "hue":color,
        'command_hue':'color',
        'saturation':255,
        'value':255,
        }
    
    # bit of a hack here, since the nexturn libs are looking for it :-(
    ns = argparse.Namespace(**kwargs)
    NHSVC(ns)
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='GEOFENCING WITH NEXTURNS')
    parser.add_argument(
        '-m', '--macaddress', type=MacAddrType, help="Mac address(s) of bulb", action='append', dest="macaddress", required=True
    )
    parser.add_argument(
        '-b', '--herehue', type=int, help="Hue for here", action='store', dest="here", required=True, default=0
    )
    parser.add_argument(
        '-c', '--notherehue', type=int, help="Hue for not here", action='store', dest="there", required=True, default=128
    )
    parser.add_argument(
        '-i', '--ipaddress', type=IPV4AddrType, help="IP Address of host", action='store', dest="ipaddress", required=True
    )
    arguments = parser.parse_args()
    argdict =  arguments.__dict__
    main(**argdict)
    
    
# note on usage
