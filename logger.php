<?php

require __DIR__ . "/vendor/autoload.php";


$url = "https://01jbacggp03tqvbhnvr0hbz40500-ed8958821260c9899ca1.requestinspector.com";

// if (empty($sip_data)) {
//     echo "There is no data !!";
//     return;
// }
// file_put_contents("sip_response.json", base64_decode($argv[1]));
// $text =base64_decode($argv[1]);


$text = file_get_contents("php://stdin");
$text = fixSIPMessage($text);

try {

    // تجزیه پیام SIP
    $response = \RTCKit\SIP\Message::parse($text);


    printf("Protocol version:   %s" . PHP_EOL, $response->version);
    printf("Request method:     %s" . PHP_EOL, $response->method);
    printf("Request URI:        %s" . PHP_EOL, $response->uri);
    printf("Via:                %s" . PHP_EOL, $response->via->values[0]->host);
    printf("Via branch:         %s" . PHP_EOL, $response->via->values[0]->branch);
    printf("From scheme:        %s" . PHP_EOL, $response->from->uri->scheme);
    printf("From user:          %s" . PHP_EOL, $response->from->uri->user);
    printf("From host:          %s" . PHP_EOL, $response->from->uri->host);
    printf("From tag:           %s" . PHP_EOL, $response->from->tag);
    printf("To scheme:          %s" . PHP_EOL, $response->to->uri->scheme);
    printf("To user:            %s" . PHP_EOL, $response->to->uri->user);
    printf("To host:            %s" . PHP_EOL, $response->to->uri->host);
    printf("Sequence number:    %s" . PHP_EOL, $response->cSeq->sequence);
    printf("Call ID:            %s" . PHP_EOL, $response->callId->value);
    echo "\r\n---------\r\n";

    if ($response->method != "INVITE") {
        return;
    }

    //echo $response->extraHeaders["remote-party-id"]->values[0];

    // تبدیل به JSON
    $jsonData = json_encode($response, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE);

    sendJsonData($jsonData);



    // ذخیره در فایل
    file_put_contents('sip_response.json', $jsonData);

    echo "JSON ذخیره شد: sip_response.json\n";

} catch (Exception $e) {
    echo "خطا در پردازش SIP: " . $e->getMessage();
}

function fixSIPMessage($sipMessage)
{
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



function sendJsonData($jsonData)
{
    global $url;
    $ch = curl_init($url);

    curl_setopt_array($ch, [
        CURLOPT_POST => true,
        CURLOPT_POSTFIELDS => json_encode($jsonData),
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_HTTPHEADER => [
            'Content-Type: application/json'
        ],
    ]);

    $response = curl_exec($ch);

    if (curl_errno($ch)) {
        echo "❌ خطای cURL: " . curl_error($ch);
    } else {
        echo "✅ پاسخ سرور: " . $response;
    }

    curl_close($ch);
}
