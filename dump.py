import subprocess
import re

# مسیر فایل PHP روی سیستم لوکال
PHP_SCRIPT = "/usr/local/php8.4/bin/php logger.php"

def extract_sip_info(line):
    """استخراج اطلاعات مهم از پیام‌های SIP"""
    if "From:" in line or "To:" in line or "Remote-Party-ID:" in line:
        return line.strip()
    return None

def send_to_php(sip_data):
    """ارسال داده‌های SIP به فایل PHP محلی"""
    try:
        process = subprocess.Popen([PHP_SCRIPT], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate(input=sip_data.encode())

        if error:
            print(f"❌ PHP Error: {error.decode()}")
        else:
            print(f"📡 PHP Output: {output.decode()}")
    except Exception as e:
        print(f"❌ Error executing PHP script: {e}")

def run_tcpdump():
    """اجرای tcpdump و پردازش خروجی آن"""
    cmd = ["sudo", "tcpdump", "-i", "any", "-A", "-n", "port", "5060"]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    flag = False
    sip_data = ""

    for line in process.stdout:
        line = line.strip()

        # بررسی شروع پیام 200 OK
        if "SIP/2.0 200 OK" in line:
            flag = True
            sip_data = ""  # پاک کردن داده‌های قبلی

        # پردازش پیام‌های موردنظر
        if flag:
            extracted_info = extract_sip_info(line)
            if extracted_info:
                sip_data += extracted_info + "\n"

        # پایان پردازش هر پیام
        if flag and line == "":
            flag = False
            if sip_data:
                print("📡 Extracted SIP Data:\n", sip_data)
                send_to_php(sip_data)

if __name__ == "__main__":
    print("🚀 Starting TCPDump Packet Sniffing on port 5060...")
    run_tcpdump()
