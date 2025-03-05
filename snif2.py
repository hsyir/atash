from scapy.all import *

def packet_callback(pkt):
    """ بررسی پکت‌های UDP برای دریافت پیام‌های SIP """
    
    if pkt.haslayer(UDP) and pkt.haslayer(Raw):
        raw_data = pkt[Raw].load  # داده خام پکت را دریافت کن

        try:
            sip_data = raw_data.decode(errors='ignore')  # تبدیل به متن خوانا
        except Exception as e:
            print(f"❌ خطای دیکد کردن داده: {e}")
            return

        # نمایش کل محتوای SIP برای Debug
        print("------ SIP Packet Received ------")
        print(sip_data)
        print("---------------------------------")

        # بررسی اینکه پیام SIP از نوع INVITE است
        if "INVITE" in sip_data:
            print("🔥 دریافت پیام SIP INVITE!")
            print(sip_data)
            print("=================================")

# اجرای اسنیفر برای شنود پکت‌های SIP در پورت 5060
print("🚀 در حال شنود پکت‌های SIP روی پورت 5060...")
sniff(prn=packet_callback, filter="udp port 5060", store=0)
