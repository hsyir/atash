<?php


require __DIR__ . "/vendor/autoload.php";

$text = file_get_contents("php://stdin");

if (empty($sip_data)) {
    echo "There is no data !!";
    return;
}

try {
    // تجزیه پیام SIP
    $response = \RTCKit\SIP\Message::parse($text);

    // تبدیل به JSON
    $jsonData = json_encode($response, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE);

    // ذخیره در فایل
    file_put_contents('sip_response.json', $jsonData);

    echo "JSON ذخیره شد: sip_response.json\n";

} catch (Exception $e) {
    echo "خطا در پردازش SIP: " . $e->getMessage();
}


?>
