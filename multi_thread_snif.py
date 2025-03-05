from scapy.all import *
import subprocess
import threading
import re

# مسیر فایل PHP روی سیستم لوکال
PHP_SCRIPT = "/usr/local/php8.4/bin/php logger.php"

def extract_sip_header(raw_data, header_name):
    """Extracts the full value of a given SIP header from raw SIP message."""
    matches = re.findall(rf"{header_name}:\s*(.*)", raw_data, re.IGNORECASE)
    if matches:
        return "\n".join(matches)  # اگر چند مقدار داشت، همه رو برگردون
    return None

def send_to_php(sip_data):
    """ارسال داده‌های SIP به فایل PHP محلی در یک Thread جداگانه"""
    def run_php():
        try:
            process = subprocess.Popen(
                ["/usr/local/php8.4/bin/php", "logger.php"],
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,  # جلوگیری از بلاک شدن
                stderr=subprocess.DEVNULL
            )
            process.communicate(input=sip_data.encode())
        except Exception as e:
            print(f"❌ Error executing PHP script: {e}")

    # ایجاد یک Thread جدید برای اجرای PHP
    thread = threading.Thread(target=run_php)
    thread.daemon = True  # پایان خودکار Thread در صورت بسته شدن اسکریپت اصلی
    thread.start()

def packet_callback(pkt):
    """Packet sniffing callback function."""
    
    if pkt.haslayer(UDP):
        if pkt[UDP].dport == 5060 or pkt[UDP].sport == 5060:
            if pkt.haslayer(Raw):
                raw_data = pkt[Raw].load.decode(errors='ignore')

                # نمایش کل محتوای SIP برای Debug
                print("------ SIP Packet Received ------")
                print(raw_data)
                print("---------------------------------")

                # ارسال داده‌ها به PHP در یک Thread جداگانه
                send_to_php(raw_data)

def start_sniffing():
    """Start sniffing packets on port 5060."""
    print("Starting to sniff packets on port 5060...")
    sniff(prn=packet_callback, filter="udp port 5060", store=0)

if __name__ == "__main__":
    start_sniffing()
