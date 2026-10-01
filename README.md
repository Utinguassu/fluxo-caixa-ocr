# 💰 Fluxo de Caixa OCR - Gestão Financeira Inteligente

> 🤖 **Desenvolvido com o auxílio do Google Gemini**, atuando como Tech Lead e Pair Programmer em todas as etapas de arquitetura, código e testes.

Projeto de desenvolvimento de software para controle financeiro pessoal, focado em automação de lançamentos via leitura de imagens (OCR) acessível via rede local.

## 🎯 Objetivo do Projeto
Criar uma ferramenta de controle de caixa responsiva (foco mobile) que permita a inserção de um saldo inicial e a dedução automática de gastos diários através do upload de prints de extratos bancários e faturas de cartão. O sistema utiliza Visão Computacional para ler os dados da imagem e atualizar o dashboard em tempo real.

## 🛠️ Tecnologias Utilizadas (Tech Stack)
* **Backend:** Python (API REST)
* **Banco de Dados:** SQLite
* **Processamento de Imagem:** Bibliotecas de OCR em Python (Tesseract/EasyOCR)
* **Frontend:** HTML5, CSS3 (Tailwind) e JavaScript Vanilla
* **Controle de Versão e Gestão:** Git, GitHub Projects (Kanban)

## 📌 Status do Projeto
🚧 Em desenvolvimento (Fase 1: Backend e Banco de Dados)

## Testes E2E com Playwright

Os testes E2E usam o Chrome e gravam vídeo e screenshot em `relatorios/evidencias_e2e/`. O pytest também gera um relatório HTML em `relatorios/`. Esses arquivos locais são ignorados pelo Git; no GitHub Actions, ficam disponíveis para download como artefato da execução.

### Preparar um clone novo no Windows

No terminal PowerShell, na raiz do repositório:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m playwright install chrome ffmpeg
```

### Executar o teste de login

Inicie o servidor em um primeiro terminal PowerShell:

```powershell
$env:JWT_SECRET_KEY = "local-e2e-secret"
.\.venv\Scripts\python.exe -m flask --app backend.app run --host 127.0.0.1 --port 5000
```

Em outro terminal, execute o cenário. `--headed` abre o Chrome visivelmente e `--slowmo 500` desacelera as ações para facilitar a observação:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/e2e/test_e2e_login.py --headed --slowmo 500
```

Para executar toda a suíte, use:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

O workflow do GitHub Actions instala as dependências Python e do navegador, inicia a aplicação, executa toda a suíte e publica os relatórios e as evidências mesmo quando algum teste falha.