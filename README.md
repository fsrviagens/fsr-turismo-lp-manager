Este projeto serve como uma prova de conceito robusta e um ativo de portfólio para a transição de carreira, focando em duas funcionalidades principais:

1.  **Landing Page Responsiva:** Uma página de vendas única, focada em conversão, com um formulário de captura de leads.
2.  **Sistema de Gerenciamento (Admin):** Uma área restrita para:
    * Gerenciar e visualizar os leads capturados.
    * Atualizar dinamicamente todo o conteúdo da landing page (títulos, descrições, preços e condições).

## 🛠️ Stack Tecnológico

* **Backend:** Python 3.11+ (com framework Django)
* **Frontend:** HTML5, Tailwind CSS (para responsividade e estética)
* **Banco de Dados/Auth:** Supabase (PostgreSQL)
* **Hospedagem:** Railway

## 📋 Modelo de Dados Inicial

**1. Lead (fsr_agencia_lead)**
| Campo | Tipo | Requisito | Propósito |
| :--- | :--- | :--- | :--- |
| `nome` | String | Obrigatório | Nome completo do potencial cliente. |
| `email` | Email | Obrigatório | E-mail de contato. |
| `telefone` | String | Obrigatório | Telefone com DDD. |
| `destino_interesse` | String | Obrigatório | Para onde o cliente deseja viajar. |
| `budget_disponivel` | String | Opcional | Faixa de orçamento (ex: R$5k - R$10k). |
| `previsao_data` | String | Opcional | Quando pretende viajar (ex: Março/2026). |
| `data_captura`| DateTime | Auto | Data/hora da submissão do formulário. |

**2. Conteúdo da Página (fsr_agencia_content)**
| Campo | Tipo | Propósito |
| :--- | :--- | :--- |
| `titulo_principal` | String | Título chamativo da oferta. |
| `subtitulo_oferta` | Texto | Descrição breve e persuasiva. |
| `descricao_completa` | Texto | Detalhes da oferta e o que está incluso. |
| `imagem_url` | String | URL para a imagem principal da oferta. |
| `valor_base` | Float | Preço de referência (ex: 2999.00). |
| `parcelamento_detalhe`| String | Detalhes do parcelamento (ex: 12x Sem Juros de R$249,92). |