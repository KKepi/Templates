<?php
declare(strict_types=1);
// 1) Vypni všechen display_errors, aby varování nešpinilo JSON
ini_set('display_errors', '0');
error_reporting(0);

// 2) Hned po startu nastav Content-Type
header('Content-Type: application/json; charset=utf-8');

// 3) Načti JWT helper
require_once __DIR__ . '/jwt.php';

// 4) Přečti JSON tělo požadavku
$body = json_decode(file_get_contents('php://input'), true) ?? [];
$username = trim($body['username'] ?? '');
$password = $body['password'] ?? '';

// 5) Načti "databázi" uživatelů
$users = json_decode(file_get_contents(__DIR__ . '/users.json'), true) ?? [];

// 6) Projdi uživatele a ověř heslo
foreach ($users as $user) {
    if ($user['username'] === $username && password_verify($password, $user['password'])) {
        $secret = 'SUPER_SECRET_KEY_CHANGE_ME';
        $payload = [
            'id'  => $user['id'],
            'sub' => $username,
            'role'=> $user['role'],
            'iat' => time(),
            'exp' => time() + 3600
        ];
        $token = jwt_encode($payload, $secret);

        http_response_code(200);
        echo json_encode(['token' => $token]);
        exit;
    }
}

// 7) Neplatné přihlášení
http_response_code(401);
echo json_encode(['error' => 'Invalid credentials']);
exit;
