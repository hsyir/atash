<?php
// خواندن داده‌های ورودی از stdin
$sip_data = file_get_contents("php://stdin");

if (!empty($sip_data)) {
    file_put_contents("sip_logs.txt", $sip_data . PHP_EOL, FILE_APPEND);
    echo "✅ Data saved to sip_logs.txt\n";
} else {
    echo "⚠️ No data received\n";
}
?>
