<?php
// =========================
// processa_cadastro.php
// =========================

// Força exibição de erros apenas em ambiente de desenvolvimento
// Em produção, deixe "off"
ini_set('display_errors', 1);
error_reporting(E_ALL);

// Acessa as credenciais do banco de dados (Render)
$db_host = getenv('DB_HOST');
$db_name = getenv('DB_NAME');
$db_user = getenv('DB_USER');
$db_pass = getenv('DB_PASS');

try {
    // Conexão via PDO
    $dsn = "pgsql:host=$db_host;dbname=$db_name;user=$db_user;password=$db_pass";
    $conn = new PDO($dsn);
    $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch (PDOException $e) {
    die("Erro na conexão com o banco de dados.");
}

// =========================
// Recebe os dados do formulário
// =========================
$nome     = trim($_POST['nome'] ?? '');
$whatsapp = trim($_POST['whatsapp'] ?? '');
$email    = trim($_POST['email'] ?? '');

// =========================
// Validação básica
// =========================
if (empty($nome) || empty($whatsapp) || empty($email)) {
    die("Erro: Todos os campos são obrigatórios.");
}

if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
    die("Erro: Endereço de e-mail inválido.");
}

// Normaliza WhatsApp: apenas números
$whatsapp = preg_replace('/\D/', '', $whatsapp);

// =========================
// Evita e-mails duplicados
// =========================
$check = $conn->prepare("SELECT COUNT(*) FROM clientes WHERE email = ?");
$check->execute([$email]);

if ($check->fetchColumn() > 0) {
    die("Erro: Esse e-mail já está cadastrado.");
}

// =========================
// Insere os dados no banco
// =========================
$sql = "INSERT INTO clientes