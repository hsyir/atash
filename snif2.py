from scapy.all import sniff, UDP, TCP

def packet_callback(pkt):
    if pkt.haslayer(UDP) or pkt.haslayer(TCP):
        print(f"Packet: {pkt.show()}")  # نمایش تمام لایه‌های پکت
        # if pkt.haslayer(Raw):
        #     print("Raw Layer Data:")
        #     print(pkt[Raw].load.decode(errors='ignore'))
        # else:
        #     print("No Raw Data in packet")

sniff(prn=packet_callback, filter="udp port 5060 or tcp port 5060", store=0)
