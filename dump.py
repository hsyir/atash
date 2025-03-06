import subprocess
import re

# مسیر فایل PHP برای لاگ کردن تماس‌ها
PHP_SCRIPT = "/usr/local/php8.4/bin/php logger.php"

def extract_sip_info(sip_data):
    """استخراج اطلاعات مهم تماس (From, To, Remote-Party-ID)"""
    headers = {
        "From": None,
        "To": None,
        "Remote-Party-ID": None
    }

    for line in sip_data.split("\n"):
        for key in headers.keys():
            match = re.search(rf"{key}:\s*(.*)", line, re.IGNORECASE)
            if match:
                headers[key] = match.group(1).strip()

    return headers if headers["From"] else None  # اطمینان از داشتن اطلاعات تماس

def send_to_php(call_info):
    """ارسال اطلاعات تماس به اسکریپت PHP"""
    sip_data = f"From: {call_info['From']}\nTo: {call_info['To']}\nRemote-Party-ID: {call_info['Remote-Party-ID']}\n"
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
    """اجرای tcpdump برای شنود تماس‌های ورودی روی پورت 5060"""
    cmd = ["sudo", "tcpdump", "-i", "any", "-A", "-n", "port", "5060"]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    flag = False
    sip_data = ""

    for line in process.stdout:
        line = line.strip()

        # بررسی آغاز یک تماس جدید (200 OK نشان‌دهنده پاسخ موفق به تماس است)
        if "SIP/2.0 200 OK" in line:
            flag = True
            sip_data = ""

        # ذخیره اطلاعات در صورت فعال بودن flag
        if flag:
            sip_data += line + "\n"

        # پایان پردازش پیام (وقتی یک خط خالی بیاید)
        if flag and line == "":
            flag = False
            call_info = extract_sip_info(sip_data)

            # فیلتر کردن فقط تماس‌های ورودی (اگر "From" وجود داشته باشد و "To" شماره داخلی باشد)
            if call_info and "From" in call_info and call_info["From"]:
                print("📞 Incoming Call Detected:")
                print(f"From: {call_info['From']}\nTo: {call_info['To']}\nRemote-Party-ID: {call_info['Remote-Party-ID']}\n")
                send_to_php(call_info)

if __name__ == "__main__":
    print("🚀 Listening for incoming SIP calls on port 5060...")
    run_tcpdump()