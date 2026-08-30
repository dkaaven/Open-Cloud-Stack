#!/bin/sh
set -eu

php -r '
$context = stream_context_create([
    "http" => [
        "timeout" => 3,
        "ignore_errors" => true,
    ],
]);

$body = @file_get_contents(
    "http://127.0.0.1/status.php",
    false,
    $context
);

if ($body === false) {
    exit(1);
}

$status = json_decode($body, true);

if (!is_array($status)) {
    exit(1);
}

if (($status["installed"] ?? false) !== true) {
    exit(1);
}

if (($status["maintenance"] ?? false) === true) {
    exit(1);
}

if (($status["needsDbUpgrade"] ?? false) === true) {
    exit(1);
}

exit(0);
'
