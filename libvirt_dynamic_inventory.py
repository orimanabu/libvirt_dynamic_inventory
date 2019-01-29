#!/usr/bin/python

import libvirt
import sys
import json
from lxml import etree
#from pprint import pprint
from argparse import ArgumentParser

DELIMITER = '%'

def get_network_bridge_pairs(conn):
#    nbinfo = [{'network': x.name(), 'bridge': x.bridgeName()} for x in conn.listAllNetworks()]
    b2n = {}
    for x in conn.listAllNetworks():
        b2n[x.bridgeName()] = x.name()
    return b2n

def main():
    usage = 'python {} --list'.format(__file__)
    argparser = ArgumentParser(usage=usage)
    argparser.add_argument('--debug', help='debug', action='store_true')
    argparser.add_argument('--list', help='list', action='store_true')
    argparser.add_argument('--host', help='hostvar', type=str, dest='hostvars')
    args = argparser.parse_args()

    if args.debug:
        print('** debug: {}'.format(args.debug))
        print('** list: {}'.format(args.list))
        print('** host: {}'.format(args.hostvars))

    conn = libvirt.open("qemu:///system")
    if conn == None:
        print('Can not open connection to hypervisor')
        sys.exit(1)

    inventory = {}
    inventory['_meta'] = {
        "hostvars": {
        }
    }

    b2n = get_network_bridge_pairs(conn)

    for vm in conn.listAllDomains():
        if vm.isActive():
            xml = etree.fromstring(vm.XMLDesc())

            bridges = xml.xpath("//devices/interface/source/@bridge")
            macs = xml.xpath("//devices/interface/mac/@address")
            mac2br = dict(zip(macs, bridges))

            intfinfo = vm.interfaceAddresses(libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_AGENT)
#            pprint(intfinfo)

            for intf in intfinfo.keys():
                addrs = intfinfo[intf].get('addrs')
                if addrs:
                    for addr in addrs:
                        if addr['type'] == 0:
                            br = mac2br.get(intfinfo[intf]['hwaddr'])
                            if br:
                                g = {
                                    "hosts": [
                                        addr['addr']
                                    ],
                                    "vars": {
                                        "ipv4addr": addr['addr'],
                                        "name": vm.name(),
                                        "bridge": br,
                                        "network": b2n[br],
                                        "type": "groupvars"
                                    }
                                }
                                inventory[vm.name() + DELIMITER + intf] = g
                                inventory[vm.name() + DELIMITER + br] = g
                                inventory[vm.name() + DELIMITER + b2n[br]] = g

                                inventory['_meta']['hostvars'][addr['addr']] = {
                                    "ipv4addr": addr['addr'],
                                    "name": vm.name(),
                                    "bridge": br,
                                    "network": b2n[br],
                                    "type": "hostvars"
                                }
    return inventory

if __name__ == '__main__':
    inventory = main()
#    pprint(inventory)
    print(json.dumps(inventory))
