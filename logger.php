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
    $message = \RTCKit\SIP\Message::parse($text);
    /* Outputs "RTCKit\SIP\Request" */
    var_dump($message);
    
    echo get_class($message) . PHP_EOL;

    print_r("Protocol version:   " . $message->version . PHP_EOL);
    print_r("Request method:     " . $message->method . PHP_EOL);
    // print_r("Request URI:        " . $message->uri . PHP_EOL);
    print_r("Via:                " . $message->via->values[0]->host . PHP_EOL);
    print_r("Via branch:         " . $message->via->values[0]->branch . PHP_EOL);
    print_r("From scheme:        " . $request->from->uri->scheme . PHP_EOL);
    print_r("From user:          " . $request->from->uri->user . PHP_EOL);
    print_r("From host:          " . $request->from->uri->host . PHP_EOL);
    print_r("From tag:           " . $request->from->tag . PHP_EOL);
    print_r("To scheme:          " . $request->to->uri->scheme . PHP_EOL);
    print_r("To user:            " . $request->to->uri->user . PHP_EOL);
    print_r("To host:            " . $request->to->uri->host . PHP_EOL);
    print_r("Sequence number:    " . $message->cSeq->sequence . PHP_EOL);
    print_r("Call ID:            " . $message->callId->value . PHP_EOL);
    if ($message->method != "INVITE") {
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
