import re
import subprocess
import threading
import requests

def send_to_api(cid, did, ext, party):
    url = "https://01jbacggp03tqvbhnvr0hbz40500-ed8958821260c9899ca1.requestinspector.com"  # آدرس API خود را وارد کنید
    data = {
        "cid": cid,
        "did": did,
        "ext": ext,
        "party": party
    }
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            print(f"Data sent successfully: {data}")
        else:
            print(f"Failed to send data: {response.status_code}")
    except Exception as e:
        print(f"Error sending data: {e}")

def capture_sip_logs():
    cmd = ["sudo", "tcpdump", "-i", "any", "-A", "-n", "port", "5060"]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    
    flag = False
    cid, did, ext, party = None, None, None, None
    
    for line in process.stdout:
        line = line.strip()
        
        if "SIP/2.0 200 OK" in line:
            flag = True
            continue
        
        if flag and "From:" in line:
            match = re.search(r'From: "?([^"]*)"? <sip:([^@]+)@', line)
            if match:
                cid = match.group(1).strip() if match.group(1) else match.group(2).strip()
        
        if flag and "To:" in line:
            match = re.search(r'To: <sip:(\d{4})@', line)  # فقط DID های ۴ رقمی
            if match:
                did = match.group(1).strip()
            else:
                flag = False  # اگر DID چهار رقمی نبود، پردازش را متوقف کن
        
        if flag and "Remote-Party-ID:" in line:
            match = re.search(r'Remote-Party-ID: "?([^"]*)"? <sip:[^>]+>;party=(\w+)', line)
            if match:
                ext, party = match.groups()
                ext = ext.strip()
                party = party.strip()
                result = f"as CID = {cid} and DID = {did} and EXT = {ext} is {party}"
                print(result)  # نمایش در Bash
                # ایجاد یک thread جدید برای ارسال داده‌ها به API
                threading.Thread(target=send_to_api, args=(cid, did, ext, party)).start()
                flag = False

if __name__ == "__main__":
    capture_sip_logs()
