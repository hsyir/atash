import re
import subprocess
import threading
import requests
from datetime import datetime

def send_to_api(cid, did, ext, party, call_id, call_time):
    url = "http://172.20.118.173/insertfar.php"  # آدرس API خود را وارد کنید
    data = {
        "call_tel": cid,
        "cc_did": did,
        "cc_ext": ext,
        "cc_party": party,
        "cc_callid": call_id,
        "call_date": call_time
    }


#     curl --location 'http://172.20.118.173/insertfar.php' \
# --header 'Content-Type: application/json' \
# --data '{  
#     "call_date": "2025-03-06 10:00:00",  
#     "call_tel": "1234567890",  
#     "cc_did": 123,  
#     "cc_ext": "456",  
#     "cc_party": "Caller Name",  
#     "cc_callid": "uniqueCallId"  
# }'

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
    cid, did, ext, party, call_id = None, None, None, None, None
    call_time = None
    
    for line in process.stdout:
        line = line.strip()
        
        if "SIP/2.0 200 OK" in line:
            flag = True
            continue
        
        if flag and "Call-ID:" in line:
            match = re.search(r"Call-ID: (\S+)", line)
            if match:
                call_id = match.group(1).strip()
                call_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")  # زمان تماس
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
                threading.Thread(target=send_to_api, args=(cid, did, ext, party, call_id, call_time)).start()
                flag = False

if __name__ == "__main__":
    capture_sip_logs()
