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
<?php
// =========================
// processa_cadastro.php
// =========================

// Força exibição de erros apenas em ambiente de desenvolvimento
// Em produção, deixe "off"
ini_set('display_errors', 1);
error_reporting(E_ALL);

// Define o cabeçalho para responder em JSON
header('Content-Type: application/json');

// =========================
// Funções de Automação
// =========================

function enviarAlertaWhatsApp($numero, $mensagem) {
    // AQUI você integraria com uma API de WhatsApp Business
    // Exemplo com Twilio, mas pode ser qualquer outra
    /*
    $client = new Twilio\Rest\Client($sid, $token);
    $client->messages->create(
        "whatsapp:$numero",
        [
            "from" => "whatsapp:$twilio_numero",
            "body" => $mensagem
        ]
    );
    */
    // Por enquanto, apenas loga a mensagem para testes
    // Em um ambiente de produção, substitua pela lógica real
    return ['status' => 'success', 'message' => "Alerta de WhatsApp enviado para $numero"];
}

function enviarEmailConfirmacao($destinatario, $nome) {
    // AQUI você integraria com uma API de e-mail (SendGrid, Brevo, etc)
    // Usar uma biblioteca como PHPMailer é uma ótima alternativa
    /*
    $email = new \SendGrid\Mail\Mail();
    $email->setFrom("contato@fsr.tur.br", "FSR Viagens");
    $email->setSubject("Sua solicitação de orçamento foi recebida!");
    $email->addTo($destinatario, $nome);
    $email->addContent(
        "text/plain", "Olá $nome, sua solicitação foi recebida com sucesso. Em breve, um consultor entrará em contato. Obrigado por escolher a FSR Viagens!"
    );
    $sendgrid = new \SendGrid(getenv('SENDGRID_API_KEY'));
    $response = $sendgrid->send($email);
    */
    // Por enquanto, apenas loga a mensagem para testes
    return ['status' => 'success', 'message' => "E-mail de confirmação enviado para $destinatario"];
}

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
    echo json_encode(['success' => false, 'message' => 'Erro na conexão com o banco de dados.']);
    exit();
}

// =========================
// Recebe os dados do formulário em JSON (do script.js)
// =========================
$json_data = file_get_contents('php://input');
$data = json_decode($json_data, true);

// Validação dos dados
if ($data === null) {
    echo json_encode(['success' => false, 'message' => 'Erro: Dados inválidos recebidos.']);
    exit();
}

$nome       = trim($data['nome'] ?? '');
$email      = trim($data['email'] ?? '');
$whatsapp   = trim($data['telefone'] ?? '');
$preferencia= trim($data['preferencia'] ?? '');
$destino    = trim($data['destino'] ?? '');
$dataIda    = trim($data['dataIda'] ?? '');
$dataVolta  = trim($data['dataVolta'] ?? '');


// =========================
// Validação básica
// =========================
if (empty($nome) || empty($whatsapp) || empty($email)) {
    echo json_encode(['success' => false, 'message' => 'Erro: Todos os campos são obrigatórios.']);
    exit();
}

if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
    echo json_encode(['success' => false, 'message' => 'Erro: Endereço de e-mail inválido.']);
    exit();
}

// Normaliza WhatsApp: apenas números
$whatsapp = preg_replace('/\D/', '', $whatsapp);

// =========================
// Evita e-mails duplicados
// =========================
$check = $conn->prepare("SELECT COUNT(*) FROM clientes WHERE email = ?");
$check->execute([$email]);

if ($check->fetchColumn() > 0) {
    echo json_encode(['success' => false, 'message' => 'Erro: Esse e-mail já está cadastrado.']);
    exit();
}

// =========================
// Insere os dados no banco
// =========================
$sql = "INSERT INTO clientes (nome, email, whatsapp, preferencia, destino, data_ida, data_volta) 
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

    // =========================
    // Funil de Vendas e Automação
    // =========================
    $mensagem_whatsapp = "Novo lead no site FSR Viagens:\nNome: $nome\nWhatsApp: $whatsapp\nTipo: $preferencia\nIDa: $dataIda\nVolta: $dataVolta\n\nEntre em contato agora!";
    
    enviarAlertaWhatsApp('61983163710', $mensagem_whatsapp);
    enviarEmailConfirmacao($email, $nome);

    // =========================
    // Resposta para o JavaScript
    // =========================
    echo json_encode(['success' => true, 'message' => 'Cadastro realizado com sucesso!']);

} catch (PDOException $e) {
    // Log do erro para depuração
    error_log("Erro no PDO: " . $e->getMessage());
    echo json_encode(['success' => false, 'message' => 'Ocorreu um erro no servidor.']);
}
