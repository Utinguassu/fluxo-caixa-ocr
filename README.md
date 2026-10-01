# 💰 Fluxo de Caixa OCR - Gestão Financeira Inteligente

> 🤖 **Desenvolvido com o auxílio do Google Gemini**, atuando como Tech Lead e Pair Programmer em todas as etapas de arquitetura, código e testes.

Projeto de desenvolvimento de software para controle financeiro pessoal, focado em automação de lançamentos via leitura de imagens (OCR) acessível via rede local.

## 🎯 Objetivo do Projeto
Criar uma ferramenta de controle de caixa responsiva (foco mobile) que permita a inserção de um saldo inicial e a dedução automática de gastos diários através do upload de prints de extratos bancários e faturas de cartão. O sistema utiliza Visão Computacional para ler os dados da imagem e atualizar o dashboard em real time.

## 🛠️ Tecnologias Utilizadas (Tech Stack)
* **Backend:** Python (API REST com Flask)
* **Banco de Dados:** SQLite (com migrações seguras e suporte a retrocompatibilidade)
* **Processamento de Imagem:** Bibliotecas de OCR em Python (Tesseract/EasyOCR)
* **Frontend:** HTML5, CSS3 (Tailwind) e JavaScript Vanilla
* **Testes e Qualidade:** Pytest (API/Unidade) e Playwright (E2E / BDD / Page Object Model)
* **Controle de Versão e Gestão:** Git, GitHub Projects (Kanban) e CI/CD via GitHub Actions

## 📌 Status do Projeto
🚧 Em desenvolvimento (Fase atual: Módulos de Autenticação, Cadastro e Testes E2E Integrados validados)

## 🧪 Testes E2E com Playwright

Os testes E2E usam o Chrome e gravam vídeo e screenshot em `relatorios/evidencias_e2e/`. O pytest também gera um relatório HTML em `relatorios/`. Esses arquivos locais são ignorados pelo Git; no GitHub Actions, ficam disponíveis para download como artefato da execução.

### Principais Fluxos Cobertos pelos Testes:
* **Fluxo de Cadastro (UI):** Criação de novo usuário diretamente pela interface visual (com validação de nome, e-mail, telefone e senha mínima).
* **Fluxo de Login e Segurança:** Validação de credenciais válidas/inválidas, armazenamento de token JWT no `localStorage` e redirecionamento para o `/dashboard`.

### Preparar um clone novo no Windows

No terminal PowerShell, na raiz do repositório:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m playwright install chrome ffmpeg

## 📚 Documentação Interativa das APIs (Swagger / OpenAPI)

A aplicação conta com documentação nativa gerada via **Flasgger (OpenAPI 2.0)**. 

### Como Acessar
Com a aplicação em execução (`python -m flask --app backend.app run`), acesse no navegador:

* **Swagger UI (Interface Interativa):** [http://localhost:5000/apidocs/](http://localhost:5000/apidocs/)
* **Especificação OpenAPI (JSON):** [http://localhost:5000/apispec_1.json](http://localhost:5000/apispec_1.json)

---

### Mapeamento de Endpoints por Tag

#### 🔑 Autenticação (`/auth`)
* `POST /cadastro` - Registro de novos usuários com captura de telefone.
* `POST /login` - Autenticação de credenciais e geração de token JWT.

#### 💰 Saldo e Motor Financeiro (`/saldo`)
* `GET /saldo` - Consulta legada do saldo atualizado.
* `GET /api/saldo` - Consulta do saldo inicial, total de débitos e saldo atualizado do usuário autenticado.
* `POST /api/saldo` - Definição do saldo inicial obrigatório (RN05).

#### 💳 Transações e Extrato (`/transacoes`)
* `POST /transacoes` - Lançamento manual de débitos.
* `GET /transacoes` - Listagem geral de transações.
* `GET /api/extrato` - Extrato detalhado da linha do tempo ordenado do mais recente para o mais antigo (RN04).

---

### 🛡️ Como Autenticar no Swagger UI
1. Faça uma requisição em `POST /login` com suas credenciais.
2. Copie o valor da chave `token` retornado no corpo da resposta.
3. No topo da página do Swagger (`http://localhost:5000/apidocs/`), clique no botão **Authorize** (cadeado).
4. No campo de valor, digite `Bearer ` seguido do seu token (exemplo: `Bearer eyJhbGciOi...`).
5. Clique em **Authorize** e feche a janela. As rotas protegidas por JWT estarão liberadas para teste direto na interface.