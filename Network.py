import subprocess
import ipaddress
import socket
import struct

'''
A class that represents a local network.
'''


class Network:
    def __init__(self):
        self.host_ip = None
        self.host_mac = None
        self.subnet_mask = '255.255.255.0'
        self.getaway_ip = None
        self.getaway_mac = None
        self.available_ips = None
        self.all_ips = None
        self.active_ips = []

    '''
    A function that fills the attributes of the network object.
    '''

    def ipconfig(self):
        with open("/proc/net/route") as fh:
            for line in fh:
                fields = line.strip().split()
                if fields[1] != '00000000' or not int(fields[3], 16) & 2:
                    continue

                self.getaway_ip = socket.inet_ntoa(struct.pack("<L", int(fields[2], 16)))

        self.host_ip = subprocess.check_output(["ip", "-o", "route", "get", "1.1.1.1"], universal_newlines=True).split(" ")[6]
        self.available_ips = [str(ip) for ip in ipaddress.IPv4Network(self.host_ip + '/' + self.subnet_mask, False)]
        self.all_ips = [str(ip) for ip in ipaddress.IPv4Network(self.host_ip + '/' + self.subnet_mask, False)]
        self.available_ips.remove(self.host_ip)
        self.available_ips.remove(self.getaway_ip)
