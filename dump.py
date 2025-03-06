import subprocess
import re

# مسیر فایل PHP برای ارسال داده‌ها
PHP_SCRIPT = "/usr/local/php8.4/bin/php logger.php"

def extract_sip_headers(raw_data):
    """استخراج اطلاعات کلیدی از پیام‌های SIP"""
    headers = {"Raw SIP Packet": raw_data.strip()}  # ذخیره کل پکت SIP

    # استخراج متد و شماره توالی
    method_match = re.search(r'^(INVITE|BYE|ACK|CANCEL|REGISTER|OPTIONS|INFO|PRACK|SUBSCRIBE|NOTIFY|PUBLISH|MESSAGE|UPDATE|REFER) SIP/2.0', raw_data, re.MULTILINE)
    seq_match = re.search(r'CSeq:\s*(\d+)\s*(\w+)', raw_data, re.IGNORECASE)

    if method_match:
        headers["Method"] = method_match.group(1)
    if seq_match:
        headers["CSeq"] = f"{seq_match.group(1)} {seq_match.group(2)}"

    # استخراج هدرهای اصلی
    for header in ["From", "To", "Remote-Party-ID"]:
        match = re.search(rf"{header}:\s*(.*)", raw_data, re.IGNORECASE)
        if match:
            headers[header] = match.group(1).strip()

    return headers

def send_to_php(sip_data):
    """ارسال داده‌های SIP به اسکریپت PHP"""
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
    """اجرای tcpdump برای شنود تماس‌های SIP"""
    print("🚀 Listening for SIP packets on port 5060...")
    cmd = ["sudo", "tcpdump", "-i", "any", "-A", "-n", "port", "5060"]
    
    with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, bufsize=1) as proc:
        raw_data = ""
        for line in proc.stdout:
            raw_data += line

            # تشخیص پایان یک پیام SIP
            if line.strip() == "":
                sip_headers = extract_sip_headers(raw_data)

                # بررسی اینکه تماس ورودی است و Remote-Party-ID دارد
                if "From" in sip_headers and "Remote-Party-ID" in sip_headers:
                    log_message = f"""
📞 Incoming Call Detected:
Method: {sip_headers.get("Method", "Unknown")}
CSeq: {sip_headers.get("CSeq", "Unknown")}
From: {sip_headers.get("From", "Unknown")}
To: {sip_headers.get("To", "Unknown")}
Remote-Party-ID: {sip_headers.get("Remote-Party-ID", "None")}

📝 Full SIP Packet:
{sip_headers["Raw SIP Packet"]}
"""
                    print(log_message)
                    # send_to_php(log_message)

                raw_data = ""  # پاک کردن داده‌های قبلی برای پردازش پیام جدید

if __name__ == "__main__":
    run_tcpdump()
