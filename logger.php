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


    print_r("Protocol version:   " . $response->version . PHP_EOL);
    print_r("Request method:     " . $response->method . PHP_EOL);
    print_r("Request URI:        " . $response->uri . PHP_EOL);
    print_r("Via:                " . $response->via->values[0]->host . PHP_EOL);
    print_r("Via branch:         " . $response->via->values[0]->branch . PHP_EOL);
    print_r("From scheme:        " . $response->from->uri->scheme . PHP_EOL);
    print_r("From user:          " . $response->from->uri->user . PHP_EOL);
    print_r("From host:          " . $response->from->uri->host . PHP_EOL);
    print_r("From tag:           " . $response->from->tag . PHP_EOL);
    print_r("To scheme:          " . $response->to->uri->scheme . PHP_EOL);
    print_r("To user:            " . $response->to->uri->user . PHP_EOL);
    print_r("To host:            " . $response->to->uri->host . PHP_EOL);
    print_r("Sequence number:    " . $response->cSeq->sequence . PHP_EOL);
    print_r("Call ID:            " . $response->callId->value . PHP_EOL);
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
