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