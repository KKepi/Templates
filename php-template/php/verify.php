<?php
declare(strict_types=1);
// Vypni výstup chyb, až když budeš vědět, že všechno funguje
ini_set('display_errors', '0');
error_reporting(0);

header('Content-Type: application/json; charset=utf-8');
require_once __DIR__ . '/jwt.php';

// 1) Získej token
$headers = getallheaders();
$auth    = $headers['Authorization'] ?? '';
$token   = preg_replace('/^Bearer\s+/i', '', $auth);

// 2) Dekóduj a ověř platnost i expiraci
$payload = jwt_decode($token, 'SUPER_SECRET_KEY_CHANGE_ME');
if (!$payload) {
    http_response_code(401);
    echo json_encode(['valid' => false]);
    exit;
}

// 3) Načti uživatele a zkontroluj, že stále existuje
$users = json_decode(file_get_contents(__DIR__.'/users.json'), true) ?: [];
$found = false;
foreach ($users as $u) {
    // pokud máš v payload `sub` ID:
    if (isset($u['id'], $payload['sub']) && $u['id'] == $payload['id']) {
        $found = true;
        break;
    }
    // nebo pokud používáš `username` claim:
    if (isset($u['username'], $payload['username']) && $u['username'] === $payload['username']) {
        $found = true;
        break;
    }
}
if (!$found) {
    http_response_code(401);
    echo json_encode(['valid' => false]);
    exit;
}

// 4) Všechno ok
echo json_encode(['valid' => true, 'payload' => $payload]);
exit;
