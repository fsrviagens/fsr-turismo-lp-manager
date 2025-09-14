<?php

// Acessar as credenciais do seu banco de dados
$servername = "localhost"; // Geralmente, o servidor local é "localhost"
$username = "seu_usuario"; // SUBSTITUA pelo seu usuário do banco de dados
$password = "sua_senha";   // SUBSTITUA pela sua senha do banco de dados
$dbname = "fsr_viagens";   // SUBSTITUA pelo nome do seu banco de dados

// Crie a conexão com o banco de dados
$conn = new mysqli($servername, $username, $password, $dbname);

// Verifique se a conexão foi bem-sucedida
if ($conn->connect_error) {
    die("Falha na conexão: " . $conn->connect_error);
}

// Receba os dados do formulário
$nome = $_POST['nome'];
$whatsapp = $_POST['whatsapp'];
$email = $_POST['email'];

// Verifique se os dados não estão vazios
if (empty($nome) || empty($whatsapp) || empty($email)) {
    echo "Erro: Todos os campos são obrigatórios.";
    $conn->close();
    exit;
}

// Prepara a query SQL para inserir os dados de forma segura
$stmt = $conn->prepare("INSERT INTO clientes (nome, whatsapp, email) VALUES (?, ?, ?)");
$stmt->bind_param("sss", $nome, $whatsapp, $email);

// Execute a query
if ($stmt->execute()) {
    echo "Cadastro realizado com sucesso!";
    // Redirecione o usuário para uma página de sucesso
    // header("Location: sucesso.html");
} else {
    echo "Erro: " . $stmt->error;
}

$stmt->close();
$conn->close();
?>
