<?php
// =========================
// processa_cadastro.php
// =========================

// Exibe erros apenas em ambiente de desenvolvimento
ini_set('display_errors', 1);
error_reporting(E_ALL);

// Define o cabeçalho para JSON
header('Content-Type: application/json');

// =========================
// Funções de Automação (mock)
// =========================
function enviarAlertaWhatsApp($numero, $mensagem) {
    // Integração real deve ser feita com Twilio, Z-API, etc.
    return ['status' => 'success', 'message' => "Alerta WhatsApp enviado para $numero"];
}

function enviarEmailConfirmacao($destinatario, $nome) {
    // Integração real deve ser feita com PHPMailer, SendGrid, Brevo, etc.
    return ['status' => 'success', 'message' => "E-mail enviado para $destinatario"];
}

// =========================
// Conexão com o banco (Render)
// =========================
$db_host = getenv('DB_HOST');
$db_name = getenv('DB_NAME');
$db_user = getenv('DB_USER');
$db_pass = getenv('DB_PASS');

try {
    $dsn = "pgsql:host=$db_host;dbname=$db_name;user=$db_user;password=$db_pass";
    $conn = new PDO($dsn);
    $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch (PDOException $e) {
    echo json_encode(['success' => false, 'message' => 'Erro na conexão com o banco de dados.']);
    exit();
}

// =========================
// Recebe os dados do formulário em JSON
// =========================
$json_data = file_get_contents('php://input');
$data = json_decode($json_data, true);

if ($data === null) {
    echo json_encode(['success' => false, 'message' => 'Erro: Dados inválidos recebidos.']);
    exit();
}

// =========================
// Sanitização e validação
// =========================
$nome        = trim($data['nome'] ?? '');
$email       = trim($data['email'] ?? '');
$whatsapp    = trim($data['telefone'] ?? ''); // No JS vem como "telefone"
$preferencia = trim($data['preferencia'] ?? '');
$destino     = trim($data['destino'] ?? '');
$dataIda     = trim($data['dataIda'] ?? '');
$dataVolta   = trim($data['dataVolta'] ?? '');

if (empty($nome) || empty($whatsapp) || empty($email)) {
    echo json_encode(['success' => false, 'message' => 'Erro: Nome, WhatsApp e E-mail são obrigatórios.']);
    exit();
}

if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
    echo json_encode(['success' => false, 'message' => 'Erro: Endereço de e-mail inválido.']);
    exit();
}

// Normaliza WhatsApp: apenas números
$whatsapp = preg_replace('/\D/', '', $whatsapp);

// =========================
// Evita duplicidade de e-mail
// =========================
$check = $conn->prepare("SELECT COUNT(*) FROM clientes WHERE email = :email");
$check->execute([':email' => $email]);

if ($check->fetchColumn() > 0) {
    echo json_encode(['success' => false, 'message' => 'Erro: Esse e-mail já está cadastrado.']);
    exit();
}

// =========================
// Insere os dados no banco
// =========================
$sql = "INSERT INTO clientes 
        (nome, email, whatsapp, preferencia, destino, data_ida, data_volta) 
        VALUES (:nome, :email, :whatsapp, :preferencia, :destino, :data_ida, :data_volta)";

try {
    $stmt = $conn->prepare($sql);
    $stmt->execute([
        ':nome'        => $nome,
        ':email'       => $email,
        ':whatsapp'    => $whatsapp,
        ':preferencia' => $preferencia,
        ':destino'     => $destino,
        ':data_ida'    => $dataIda,
        ':data_volta'  => $dataVolta,
    ]);

    // Dispara automações
    $mensagem_whatsapp = "Novo lead no site FSR Viagens:\n".
                         "Nome: $nome\n".
                         "WhatsApp: $whatsapp\n".
                         "Tipo: $preferencia\n".
                         "Destino: $destino\n".
                         "Ida: $dataIda | Volta: $dataVolta";

    enviarAlertaWhatsApp('61983163710', $mensagem_whatsapp);
    enviarEmailConfirmacao($email, $nome);

    echo json_encode(['success' => true, 'message' => 'Cadastro realizado com sucesso!']);
} catch (PDOException $e) {
    error_log("Erro no PDO: " . $e->getMessage());
    echo json_encode(['success' => false, 'message' => 'Erro ao salvar no banco de dados.']);
}