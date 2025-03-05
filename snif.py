from scapy.all import *
import subprocess
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
    """ارسال داده‌های SIP به فایل PHP محلی"""
    try:
        process = subprocess.Popen(["/usr/local/php8.4/bin/php", "logger.php"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate(input=sip_data.encode())

        if error:
            print(f"❌ PHP Error: {error.decode()}")
        else:
            print(f"📡 PHP Output: {output.decode()}")
    except Exception as e:
        print(f"❌ Error executing PHP script: {e}")

def packet_callback(pkt):
    """Packet sniffing callback function."""
    print("---------callback--------")
    if pkt.haslayer(UDP):
        if pkt[UDP].dport == 5060 or pkt[UDP].sport == 5060:
            if pkt.haslayer(Raw):
                raw_data = pkt[Raw].load.decode(errors='ignore')

                # نمایش کل محتوای SIP برای Debug
                print("------ SIP Packet Received ------")
                print(raw_data)
                print("---------------------------------")
                print("")
                print("")
                print("")

                # ارسال کل محتوای SIP به PHP
                #send_to_php(raw_data)

def start_sniffing():
    """Start sniffing packets on port 5060."""
    print("Starting to sniff packets on port 5060...")
    sniff(prn=packet_callback, filter="udp port 5060", store=0)

if __name__ == "__main__":
    start_sniffing()
