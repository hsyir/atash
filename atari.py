import re
import subprocess

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
                flag = False

if name == "main":
    capture_sip_logs()