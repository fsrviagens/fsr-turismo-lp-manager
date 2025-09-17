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

    orcamentoForm.addEventListener('submit', (e) => {
        e.preventDefault(); // Impede o envio padrão do formulário

        // Aqui é onde a sua API de back-end entrará.
        // Por enquanto, vamos simular o envio de dados.
        const formData = {
            nome: document.getElementById('nome').value,
            email: document.getElementById('email').value,
            telefone: document.getElementById('telefone').value,
            preferencia: document.getElementById('preferencia').value,
            destino: document.getElementById('destino').value,
            dataIda: document.getElementById('dataIda').value,
            dataVolta: document.getElementById('dataVolta').value,
        };

        // Simulação de envio para um servidor
        console.log('Dados do formulário para envio:', formData);
        
        // Em um projeto real, você usaria 'fetch' para enviar os dados para o servidor:
        /*
        fetch('https://sua-api.com/orcamentos', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData),
        })
        .then(response => response.json())
        .then(data => {
            console.log('Sucesso:', data);
            alert('Orçamento solicitado com sucesso!');
            orcamentoForm.reset();
        })
        .catch((error) => {
            console.error('Erro:', error);
            alert('Ocorreu um erro ao solicitar o orçamento. Tente novamente.');
        });
        */

        // Por enquanto, apenas exibe uma mensagem de sucesso
        alert('Orçamento solicitado com sucesso! A equipe FSR Viagens entrará em contato.');
        orcamentoForm.reset();
    });
});
