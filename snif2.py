from scapy.all import sniff, UDP, TCP, Raw, IP

def packet_callback(pkt):
    # بررسی اینکه آیا پکت UDP یا TCP است
    if pkt.haslayer(UDP) or pkt.haslayer(TCP):
        print(f"\n---- New Packet ----")
        print(f"Packet Summary: {pkt.summary()}")

        # بررسی و نمایش تمام لایه‌های پکت
        # print("Full Packet Information:")
        # pkt.show()

        # بررسی لایه Raw (برای داده‌های متن خام)
        if pkt.haslayer(Raw):
            print("\nRaw Layer Data:")
            try:
                print(pkt[Raw].load.decode(errors='ignore'))  # تلاش برای دیکد کردن داده‌های Raw
            except Exception as e:
                print(f"Error decoding Raw data: {e}")
        else:
            print("No Raw Layer in packet")

        # بررسی پروتکل UDP/TCP برای پکت‌های SIP (پورت 5060)
        if pkt.haslayer(UDP):
            if pkt[UDP].dport == 5060 or pkt[UDP].sport == 5060:
                print("\nUDP SIP Packet Found:")
                if b"INVITE" in pkt[Raw].load:
                    print("Found SIP INVITE packet!")
        elif pkt.haslayer(TCP):
            if pkt[TCP].dport == 5060 or pkt[TCP].sport == 5060:
                print("\nTCP SIP Packet Found:")
                if b"INVITE" in pkt[Raw].load:
                    print("Found SIP INVITE packet!")

        # بررسی پورت‌های دیگر برای SIP (در صورت استفاده از پورت غیر 5060)
        if pkt.haslayer(IP):
            if pkt[IP].src != "127.0.0.1" and pkt[IP].dst != "127.0.0.1":
                print(f"External Traffic Detected: {pkt[IP].src} -> {pkt[IP].dst}")

    else:
        print("\nNon-UDP/TCP Packet detected.")

def start_sniffing():
    print("Starting packet sniffing...")
    sniff(prn=packet_callback, filter="udp or tcp", store=0)

if __name__ == "__main__":
    start_sniffing()
