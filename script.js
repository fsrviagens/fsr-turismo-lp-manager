// Aguarda o documento HTML ser totalmente carregado
document.addEventListener('DOMContentLoaded', () => {

    // Gerenciamento de Modais
    const modalButtons = document.querySelectorAll('.btn-detail');
    const closeButtons = document.querySelectorAll('.close-btn');

    modalButtons.forEach(button => {
        button.addEventListener('click', (event) => {
            const modalId = button.getAttribute('aria-controls');
            const modal = document.getElementById(modalId);
            if (modal) {
                modal.style.display = 'block';
                // Opcional: mover o foco para o modal para melhorar a acessibilidade
                modal.focus();
            }
        });
    });

    closeButtons.forEach(button => {
        button.addEventListener('click', (event) => {
            const modal = button.closest('.modal');
            if (modal) {
                modal.style.display = 'none';
                // Opcional: retornar o foco para o botão que abriu o modal
                document.getElementById(modal.getAttribute('aria-labelledby')).focus();
            }
        });
    });

    window.addEventListener('click', (event) => {
        if (event.target.classList.contains('modal')) {
            event.target.style.display = 'none';
        }
    });

    // Gerenciamento do Formulário
    const form = document.getElementById('orcamentoForm');
    form.addEventListener('submit', (event) => {
        event.preventDefault(); // Impede o envio padrão do formulário

        // Aqui você adicionaria a lógica de validação do formulário
        if (validarFormulario()) {
            // Se o formulário for válido, envie os dados
            // Futuramente, você fará isso para um back-end
            console.log('Formulário enviado com sucesso!');
            form.reset(); // Limpa o formulário
        } else {
            console.log('Por favor, preencha todos os campos corretamente.');
        }
    });

    function validarFormulario() {
        const nome = document.getElementById('nome').value;
        const email = document.getElementById('email').value;
        const telefone = document.getElementById('telefone').value;

        // Exemplo simples de validação:
        if (nome === '' || email === '' || telefone === '') {
            return false;
        }

        // Adicionar validação de formato de e-mail e telefone se necessário
        return true;
    }
});
