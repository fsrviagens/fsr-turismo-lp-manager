<?php

// Acessar as credenciais do seu banco de dados a partir das variáveis de ambiente do Render
$db_host = getenv('DB_HOST');
$db_name = getenv('DB_NAME');
$db_user = getenv('DB_USER');
$db_pass = getenv('DB_PASS');

// Crie a conexão com o banco de dados usando PDO para PostgreSQL
try {
    $dsn = "pgsql:host=$db_host;dbname=$db_name;user=$db_user;password=$db_pass";
    $conn = new PDO($dsn);
    $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch (PDOException $e) {
    die("Falha na conexão: " . $e->getMessage());
}

// Receba os dados do formulário
$nome = $_POST['nome'];
$whatsapp = $_POST['whatsapp'];
$email = $_POST['email'];

// Verifique se os dados não estão vazios
if (empty($nome) || empty($whatsapp) || empty($email)) {
    echo "Erro: Todos os campos são obrigatórios.";
    exit;
}

// Prepara a query SQL para inserir os dados de forma segura
$sql = "INSERT INTO clientes (nome, whatsapp, email) VALUES (?, ?, ?)";
$stmt = $conn->prepare($sql);

// Execute a query
if ($stmt->execute([$nome, $whatsapp, $email])) {
    echo "Cadastro realizado com sucesso!";
    // Redirecione o usuário para uma página de sucesso
    // header("Location: sucesso.html");
} else {
    echo "Erro: " . $stmt->errorInfo()[2];
}

// O PDO não precisa de um método de fechamento explícito, pois a conexão é encerrada automaticamente.

?>
