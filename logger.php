<?php

require __DIR__ . "/vendor/autoload.php";

// if (empty($sip_data)) {
//     echo "There is no data !!";
//     return;
// }
file_put_contents("sip_response.json", base64_decode($argv[1]));
$text =base64_decode($argv[1]);
$text = fixSIPMessage($text);

try {

    // تجزیه پیام SIP
    $response = \RTCKit\SIP\Message::parse($text);
    echo $response->extraHeaders["remote-party-id"]->values[0];

    // تبدیل به JSON
    $jsonData = json_encode($response, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE);

    // ذخیره در فایل
    file_put_contents('sip_response.json', $jsonData);

    echo "JSON ذخیره شد: sip_response.json\n";

} catch (Exception $e) {
    echo "خطا در پردازش SIP: " . $e->getMessage();
}

function fixSIPMessage($sipMessage) {
    // جداسازی هدرها و بدنه پیام
    list($headers, $body) = explode("\r\n\r\n", $sipMessage, 2) + [null, ''];

    // بررسی مقدار Content-Length
    if (preg_match('/Content-Length:\s*(\d+)/i', $headers, $matches)) {
        $expectedLength = (int)$matches[1];
        $actualLength = strlen($body);

        // اگر مقدار Content-Length اشتباه باشد، اصلاحش می‌کنیم
        if ($actualLength !== $expectedLength) {
            $headers = preg_replace('/(Content-Length:\s*)\d+/i', "Content-Length: $actualLength", $headers);
        }
    }

    // اطمینان از اینکه بین هدرها و بدنه حتماً "\r\n\r\n" وجود دارد
    return $headers . "\r\n\r\n" . $body;
}

?>
