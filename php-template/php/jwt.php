<?php
// jwt.php
function base64url_encode($data) {
    return rtrim(strtr(base64_encode($data), '+/', '-_'), '=');
}
function base64url_decode($data) {
    return base64_decode(strtr($data, '-_', '+/'));
}
function jwt_encode(array $payload, string $secret, string $alg = 'HS256'): string {
    $header = ['typ' => 'JWT', 'alg' => $alg];
    $segments = [
        base64url_encode(json_encode($header)),
        base64url_encode(json_encode($payload))
    ];
    $signing_input = implode('.', $segments);
    $signature = hash_hmac('sha256', $signing_input, $secret, true);
    $segments[] = base64url_encode($signature);
    return implode('.', $segments);
}
function jwt_decode(string $jwt, string $secret): ?array {
    $parts = explode('.', $jwt);
    if (count($parts) !== 3) return null;
    [$header64, $payload64, $sig64] = $parts;
    $signing_input = "$header64.$payload64";
    $expected_sig = base64url_encode(hash_hmac('sha256', $signing_input, $secret, true));
    if (!hash_equals($expected_sig, $sig64)) return null;
    $payload = json_decode(base64url_decode($payload64), true);
    if (!$payload || ($payload['exp'] ?? 0) < time()) return null;
    return $payload;
}
