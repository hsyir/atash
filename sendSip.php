<?php

$sip_text = <<<SIPtext
SIP/2.0 200 OK
Via: SIP/2.0/UDP 172.20.118.99:5060;branch=z9hG4bK097681d6;rport
From: "2179491110" <sip:SimoTel%20%3CSimoTel%3E@172.20.118.99>;tag=as0b51d480
To: <sip:7580@172.20.125.71:5060>;tag=7514947~cebb7f50-2ebf-4525-bd7d-e4b809198081-34633460
Date: Sun, 02 Mar 2025 06:10:47 GMT
Call-ID: 4da608291852cb9f298000a56a38993b@172.20.118.99:5060
CSeq: 102 INVITE
Allow: INVITE, OPTIONS, INFO, BYE, CANCEL, ACK, PRACK, UPDATE, REFER, SUBSCRIBE, NOTIFY
Allow-Events: presence, kpml
Supported: replaces
Server: Cisco-CUCM11.5
Call-Info: <urn:x-cisco-remotecc:callinfo>;x-cisco-video-traffic-class=DESKTOP
Supported: X-cisco-srtp-fallback
Supported: Geolocation
Session-Expires:  1800;refresher=uas
Require:  timer
Session-ID: cd16f3ed04ba41f183770eaa34876455;remote=49f9b810d6f534b45d3d9d8ab7514947
P-Asserted-Identity: "IT-Salmani 7575" <sip:7580@172.20.125.71>
Remote-Party-ID: "IT-Salmani 7575" <sip:7580@172.20.125.71>;party=called;screen=yes;privacy=off
Contact: <sip:7580@172.20.125.71:5060>
Content-Type: application/sdp
Content-Length: 228
SIPtext;



$sipPacketEscaped = base64_encode($sip_text);
// اجرای b.php و ارسال پارامتر
$res =  exec("php logger.php $sipPacketEscaped");

echo $res;


exit;
// استفاده از shell_exec برای ارسال داده‌ها به فایل `receive_sip.php`
$command = "php " . __DIR__ . '/logger.php "' . addslashes($sip_text) . '" > /dev/null 2>&1 &';
$response = shell_exec($command);

echo "📡 Response from receive_sip.php: $response";
?>
