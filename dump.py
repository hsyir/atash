import subprocess
import re

# مسیر فایل PHP برای لاگ کردن تماس‌ها
PHP_SCRIPT = "/usr/local/php8.4/bin/php logger.php"

# لیست هدرهایی که می‌خواهیم استخراج کنیم
HEADERS = [
    "From", "To", "Remote-Party-ID", "Call-ID", "CSeq",
    "User-Agent", "Contact", "Via", "Allow", "Supported"
]

def extract_sip_info(sip_data):
    """استخراج اطلاعات کلیدی از پیام SIP"""
    extracted_info = {}

    for header in HEADERS:
        match = re.findall(rf"{header}:\s*(.*)", sip_data, re.IGNORECASE)
        if match:
            extracted_info[header] = "\n".join(match)  # اگر چند مقدار وجود داشت، همه را ذخیره کن

    # متد SIP (اولین کلمه قبل از "SIP/2.0")
    method_match = re.match(r"(\w+)\s+SIP/2.0", sip_data)
    if method_match:
        extracted_info["Method"] = method_match.group(1)

    return extracted_info if extracted_info.get("Remote-Party-ID") else None  # فقط تماس‌هایی که Remote-Party-ID دارند

def send_to_php(call_info):
    """ارسال اطلاعات تماس به اسکریپت PHP"""
    sip_data = "\n".join([f"{key}: {value}" for key, value in call_info.items()])
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

        # بررسی آغاز یک پیام جدید (خطی که متد SIP را مشخص می‌کند)
        if re.match(r"\w+\s+SIP/2.0", line):
            flag = True
            sip_data = line + "\n"
        elif flag:
            sip_data += line + "\n"

        # پایان پردازش پیام (خط خالی)
        if flag and line == "":
            flag = False
            call_info = extract_sip_info(sip_data)

            if call_info:
                print("📞 Incoming Call Detected:")
                for key, value in call_info.items():
                    print(f"{key}: {value}")
                print("-" * 40)
                
                send_to_php(call_info)

if __name__ == "__main__":
    print("🚀 Listening for incoming SIP calls on port 5060...")
    run_tcpdump()
