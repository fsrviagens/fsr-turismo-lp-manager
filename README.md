# fsr-turismo-lp-manager

Este projeto serve como uma prova de conceito robusta e um ativo de portfólio para a transição de carreira, focando em duas funcionalidades principais:

1.  **Landing Page Responsiva:** Uma página de vendas única, focada em conversão, com um formulário de captura de *leads*.
2.  **Sistema de Gerenciamento (Admin):** Uma área restrita para:
    * Gerenciar e visualizar os *leads* capturados.
    * Atualizar dinamicamente todo o conteúdo da *landing page* (títulos, descrições, preços e condições).

---

## 🛠️ Stack Tecnológico

| Componente | Tecnologia | Propósito |
| :--- | :--- | :--- |
| **Backend** | Python 3.11+ (com framework **Django**) | Lógica de negócios e API para o sistema de gerenciamento. |
| **Frontend** | HTML5, **Tailwind CSS** | Estrutura, responsividade e estética da *Landing Page* e da área Admin. |
| **Banco de Dados/Auth** | **Supabase** (PostgreSQL) | Serviço *serverless* para o banco de dados e autenticação de usuários da área Admin. |
| **Hospedagem Principal** | **Railway** | Plataforma para hospedagem da aplicação Django, ideal para projetos em Python/Django. |

---

## 🚀 Arquitetura de Produção e Deployment (DevOps)

Esta arquitetura foi desenhada para ser moderna, escalável e com baixo custo de manutenção, alinhada com as melhores práticas de *cloud-native*:

* **Aplicação (Django):** Hospedada no **Railway**, utilizando a integração direta com o GitHub para um fluxo de **CI/CD** (*Continuous Integration/Continuous Delivery*). Qualquer *push* na *branch* principal (`main`) dispara o *build* e o *deployment* automático.
* **Banco de Dados/Auth:** Gerenciado pelo **Supabase**, desacoplando a gestão de dados da infraestrutura da aplicação.
* **Conteúdo Estático/Mídia (Imagens/Arquivos):** Utiliza o **Cloudflare R2** (armazenamento de objetos S3-like). Isso é crucial para:
    * **Performance:** Serve arquivos estáticos e imagens diretamente através da CDN global do Cloudflare.
    * **Escalabilidade:** Descarrega o Railway de servir arquivos, que deve focar apenas na lógica da aplicação.

---

## 📋 Modelo de Dados Inicial

O projeto inicia com duas entidades principais para suportar as funcionalidades propostas.

### 1. Lead (fsr\_agencia\_lead)

| Campo | Tipo | Requisito | Propósito |
| :--- | :--- | :--- | :--- |
| `nome` | String | Obrigatório | Nome completo do potencial cliente. |
| `email` | Email | Obrigatório | E-mail de contato e chave de comunicação. |
| `telefone` | String | Obrigatório | Telefone com DDD. |
| `destino_interesse` | String | Obrigatório | Para onde o cliente deseja viajar. |
| `budget_disponivel` | String | Opcional | Faixa de orçamento (ex: R$5k - R$10k). |
| `previsao_data` | String | Opcional | Quando pretende viajar (ex: Março/2026). |
| `data_captura` | DateTime | Auto | Data/hora da submissão do formulário.

### 2. Conteúdo da Página (fsr\_agencia\_content)

| Campo | Tipo | Propósito |
| :--- | :--- | :--- |
| `titulo_principal` | String | Título chamativo da oferta. |
| `subtitulo_oferta` | Texto | Descrição breve e persuasiva. |
| `descricao_completa` | Texto | Detalhes da oferta e o que está incluso. |
| `imagem_url` | String | URL para a imagem principal da oferta. |
| `valor_base` | Float | Preço de referência (ex: 2999.00). |
| `parcelamento_detalhe` | String | Detalhes do parcelamento (ex: 12x Sem Juros de R$249,92).
