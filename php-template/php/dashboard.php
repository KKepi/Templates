<?php
declare(strict_types=1);
ini_set('display_errors', '0');
error_reporting(0);

// ====================================== KONTROLA JWT TOKENU ======================================
require_once __DIR__ . '/jwt.php';

// --- 1) Ověření tokenu a role ---
$headers = getallheaders();
$token   = $headers['Authorization'] 
           ?? ($_GET['token'] ?? '');
$token   = preg_replace('/^Bearer\s+/i', '', $token);

$secret  = 'SUPER_SECRET_KEY_CHANGE_ME';
$payload = jwt_decode($token, $secret);

if (!$payload) {
    header('Location: index.html');
    exit;
}
// =================================================================================================

// ====================================== NAČTENÍ DAT Z TOKENU =====================================
$userId   = $payload['id']; // ID uživatele --- DŮLEŽITÉ VLOŽIT VŠUDE KDYŽ NAČTU JWT
$username = htmlspecialchars($payload['sub'], ENT_QUOTES, 'UTF-8');
$role     = $payload['role'];
$maxId = 0;
foreach ($users as $u) {
    if (!empty($u['id']) && $u['id'] > $maxId) {
        $maxId = $u['id'];
    }
}
$newId = $maxId + 1;
// =================================================================================================

// --- 2) Zpracování registrace (pouze pro adminy) ---
$feedback = '';
if ($_SERVER['REQUEST_METHOD'] === 'POST' && $role === 'admin') {
    $newUser = trim($_POST['new_username'] ?? '');
    $newPass = $_POST['new_password'] ?? '';
    $newRole = $_POST['new_role'] ?? '';

    if ($newUser === '' || $newPass === '' || !in_array($newRole, ['admin','user'], true)) {
        $feedback = 'Vyplňte všechna pole správně.';
    } else {
        $file = __DIR__ . '/users.json';
        $users = json_decode(file_get_contents($file), true) ?: [];

        // Kontrola duplicitního uživatele
        $exists = false;
        foreach ($users as $u) {
            if ($u['username'] === $newUser) {
                $exists = true;
                break;
            }
        }
        if ($exists) {
            $feedback = 'Uživatel s tímto jménem již existuje.';
        } else {
            // Hashování hesla
            $hash = password_hash($newPass, PASSWORD_DEFAULT);
            $users[] = [
                'id'       => $newId,
                'username' => $newUser,
                'password' => $hash,
                'role'     => $newRole
            ];
            // Bezpečný zápis
            $json = json_encode($users, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE);
            if (file_put_contents($file, $json, LOCK_EX) !== false) {
                $feedback = 'Uživatel úspěšně zaregistrován.';
            } else {
                $feedback = 'Chyba při zápisu do users.json.';
            }
        }
    }
}
?>
<!DOCTYPE html>
<html lang="cs">
<head>
  <meta charset="UTF-8">
  <title>Dashboard</title>
  <style>
    body { font-family: sans-serif; max-width: 600px; margin: 2rem auto; }
    .feedback { margin: 1rem 0; color: green; }
    .error    { color: #d32f2f; }
    form { border: 1px solid #ccc; padding: 1rem; border-radius: 8px; }
    label { display: block; margin: .5rem 0 .2rem; }
    input, select { width: 100%; padding: .5rem; margin-bottom: .5rem; }
    button { padding: .5rem 1rem; background: #1976d2; color: #fff; border: none; border-radius: 4px; cursor: pointer; }
  </style>
</head>
<body>

  <h1>Vítej, <?php echo $username; ?>!</h1>
  <h1>Vítej, <?php echo $userId; ?>!</h1>
  <p>Tvoje role: <strong><?php echo htmlspecialchars($role, ENT_QUOTES, 'UTF-8'); ?></strong></p>
  <button onclick="logout()">Odhlásit</button>

  <?php if ($role === 'admin'): ?>
    <h2>Registrace nového uživatele</h2>
    <?php if ($feedback): ?>
      <div class="feedback <?php echo strpos($feedback, 'Chyba') === 0 ? 'error' : ''; ?>">
        <?php echo htmlspecialchars($feedback, ENT_QUOTES, 'UTF-8'); ?>
      </div>
    <?php endif; ?>
    <form method="POST" novalidate>
      <label for="new_username">Uživatelské jméno</label>
      <input type="text" id="new_username" name="new_username" required>

      <label for="new_password">Heslo</label>
      <input type="password" id="new_password" name="new_password" required>

      <label for="new_role">Role</label>
      <select id="new_role" name="new_role">
        <option value="user">Uživatel</option>
        <option value="admin">Admin</option>
      </select>

      <button type="submit">Registrovat</button>
    </form>
  <?php endif; ?>

  <?php if ($role === 'user'): ?>
    <h2>Zatím pro tebe neexistuje žádná funkce</h2>
  <?php endif; ?>

  <script>
    function logout() {
      localStorage.removeItem('jwt');
      location.href = 'index.html';
    }
    // Ověření tokenu při načtení stránky
    fetch('verify.php', {
      headers: { 'Authorization': 'Bearer ' + localStorage.getItem('jwt') }
    }).then(res => {
      if (!res.ok) logout();
    });
  </script>
</body>
</html>
