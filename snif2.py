from scapy.all import *

def packet_callback(pkt):
    if pkt.haslayer(UDP) and pkt.haslayer(Raw):
        sip_data = pkt[Raw].load.decode()

        # استخراج اولین خط پیام برای تشخیص متد
        first_line = sip_data.split("\n")[0]

        if first_line.startswith("INVITE"):
            print("🔥 دریافت پیام SIP INVITE!")
            print(sip_data)
        elif first_line.startswith("OPTIONS"):
            print("📡 دریافت پیام SIP OPTIONS!")
        else:
            print("📦 دریافت پیام دیگر:", first_line)

sniff(prn=packet_callback, filter="udp port 5060", store=0)