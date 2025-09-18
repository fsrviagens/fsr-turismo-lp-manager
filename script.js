// Aguarda o carregamento completo do DOM
document.addEventListener('DOMContentLoaded', () => {

    //
    // LÓGICA DO MODAL
    //
    const modalButtons = document.querySelectorAll('.btn--detail');
    const modalCloseButtons = document.querySelectorAll('.modal__close');
    const modals = document.querySelectorAll('.modal');

    // Abre o modal
    const openModal = (modalId) => {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('is-active');
            // Foca no botão de fechar para acessibilidade
            modal.querySelector('.modal__close').focus();
        }
    };

    // Fecha o modal
    const closeModal = (modal) => {
        if (modal) {
            modal.classList.remove('is-active');
        }
    };

    // Adiciona o ouvinte de evento para abrir os modais
    modalButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            const modalId = e.target.getAttribute('aria-controls');
            openModal(modalId);
        });
    });

    // Adiciona o ouvinte de evento para fechar os modais
    modalCloseButtons.forEach(button => {
        button.addEventListener('click', () => {
            const modal = button.closest('.modal');
            closeModal(modal);
        });
    });

    // Fecha o modal ao clicar fora dele
    window.addEventListener('click', (e) => {
        modals.forEach(modal => {
            if (e.target === modal) {
                closeModal(modal);
            }
        });
    });

    //
    // LÓGICA DO FORMULÁRIO (futuro back-end)
    //
    const orcamentoForm = document.getElementById('orcamentoForm');

    orcamentoForm.addEventListener('submit', async (e) => { // Use 'async' para o 'await' do fetch
        e.preventDefault(); // Impede o envio padrão do formulário

        // 1. Validação de Formulário
        const nome = document.getElementById('nome').value.trim();
        const email = document.getElementById('email').value.trim();
        const telefone = document.getElementById('telefone').value.trim();
        const dataIda = document.getElementById('dataIda').value;
        const dataVolta = document.getElementById('dataVolta').value;

        // Validação de campos obrigatórios
        if (!nome || !email || !telefone || !dataIda || !dataVolta) {
            alert('Por favor, preencha todos os campos obrigatórios.');
            return;
        }

        // Validação de formato de e-mail (usando regex simples)
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            alert('Por favor, insira um e-mail válido.');
            return;
        }

        // Validação de datas
        const dataIdaObj = new Date(dataIda);
        const dataVoltaObj = new Date(dataVolta);
        if (dataIdaObj >= dataVoltaObj) {
            alert('A data de volta deve ser posterior à data de ida.');
            return;
        }

        const formData = {
            nome: nome,
            email: email,
            telefone: telefone,
            preferencia: document.getElementById('preferencia').value,
            destino: document.getElementById('destino').value,
            dataIda: dataIda,
            dataVolta: dataVolta,
        };

        // 2. Envio Assíncrono para o Backend
        try {
            const response = await fetch('processa_cadastro.php', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData),
            });

            if (!response.ok) {
                throw new Error('Erro no servidor. Tente novamente mais tarde.');
            }

            const data = await response.json();

            // 3. Feedback ao Usuário
            if (data.success) {
                alert('Orçamento solicitado com sucesso! A equipe FSR Viagens entrará em contato.');
                orcamentoForm.reset();
            } else {
                alert('Ocorreu um erro ao solicitar o orçamento. Por favor, tente novamente.');
            }

        } catch (error) {
            console.error('Erro:', error);
            alert('Ocorreu um erro na comunicação com o servidor. Tente novamente.');
        }
    });
});
