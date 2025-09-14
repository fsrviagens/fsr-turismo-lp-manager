function openModal(id) {
    const modal = document.getElementById(id);
    modal.style.display = 'flex';
    document.body.style.overflow = 'hidden'; // Evita rolagem da página quando o modal está aberto
}

function closeModal(id) {
    const modal = document.getElementById(id);
    modal.style.display = 'none';
    document.body.style.overflow = 'auto'; // Restaura a rolagem
}

// Fecha o modal ao clicar fora dele
window.onclick = function(event) {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        if (event.target === modal) {
            modal.style.display = 'none';
            document.body.style.overflow = 'auto';
        }
    });
}

document.getElementById('orcamentoForm').addEventListener('submit', function(e) {
    e.preventDefault();

    const form = e.target;
    const nome = form.nome.value;
    const email = form.email.value;
    const telefone = form.telefone.value;
    const preferencia = form.preferencia.value;
    const destino = form.destino.value || 'Não informado';
    const dataIda = form.dataIda.value;
    const dataVolta = form.dataVolta.value;

    // Validação de datas
    const ida = new Date(dataIda);
    const volta = new Date(dataVolta);
    
    if (ida > volta) {
        alert("A data de retorno não pode ser anterior à data de partida!");
        return;
    }

    let message = `*Novo Lead FSR Viagens*\n\n`;
    message += `*Nome:* ${nome}\n`;
    message += `*Email:* ${email}\n`;
    message += `*Telefone:* ${telefone}\n`;
    message += `*Preferência:* ${preferencia.charAt(0).toUpperCase() + preferencia.slice(1)}\n`;
    message += `*Destino:* ${destino}\n`;
    message += `*Período:* De ${dataIda} a ${dataVolta}\n\n`;
    message += `_Este lead foi capturado através do formulário de orçamento no site. Funil de Vendas: ${preferencia.toUpperCase()}_`;

    const whatsappUrl = `https://wa.me/5561983163710?text=${encodeURIComponent(message)}`;
    
    window.open(whatsappUrl, '_blank');
});
document.getElementById('cadastroForm').addEventListener('submit', function(e) {
    e.preventDefault();

    const form = e.target;
    const nome = form.nome.value;
    const whatsapp = form.whatsapp.value;
    const email = form.email.value;

    alert(`Olá, ${nome}! Seu cadastro foi recebido com sucesso. Em breve, enviaremos informações para o seu WhatsApp e e-mail.`);

    // Você pode adicionar a lógica de envio para o seu backend PHP aqui no futuro.
    // Exemplo:
    /*
    fetch('processa_cadastro.php', {
        method: 'POST',
        body: new URLSearchParams({
            nome: nome,
            whatsapp: whatsapp,
            email: email
        })
    });
    */

    form.reset();
});
