import uuid

import pytest

from backend.database import conectar_banco
from tests.e2e.pages.dashboard_page import DashboardPage
from tests.e2e.pages.login_page import LoginPage


BASE_URL = "http://localhost:5000"


@pytest.fixture
def massa_usuario_dinamico():
    """Gera dados únicos para a UI, sem inserir no banco, e limpa após o teste."""
    codigo_unico = uuid.uuid4().hex[:8]
    dados = {
        "nome": "Usuario Teste UI",
        "email": f"teste_ui_{codigo_unico}@fluxocaixa.com",
        "telefone": "(11) 98888-7777",
        # A tela de login limita o PIN a seis caracteres.
        "senha": "123456",
    }

    yield dados

    conexao = conectar_banco()
    try:
        conexao.execute(
            "DELETE FROM transacoes "
            "WHERE usuario_id IN (SELECT id FROM usuarios WHERE email = ?)",
            (dados["email"],),
        )
        conexao.execute(
            "DELETE FROM historico_saldos "
            "WHERE usuario_id IN (SELECT id FROM usuarios WHERE email = ?)",
            (dados["email"],),
        )
        conexao.execute(
            "DELETE FROM saldos "
            "WHERE usuario_id IN (SELECT id FROM usuarios WHERE email = ?)",
            (dados["email"],),
        )
        conexao.execute("DELETE FROM usuarios WHERE email = ?", (dados["email"],))
        conexao.commit()
    finally:
        conexao.close()


def test_login_interface_e_falha(page):
    """
    Cenário (BDD): Usuário tenta fazer login com dados incorretos e vê o alerta.

    Dado (Given) que o usuário acessa a tela de Login
    E (And) visualiza a mensagem de "Bem-vindo ao projeto"
    Quando (When) ele preencher um e-mail e senha inválidos
    E (And) clicar em 'Acessar Sistema'
    Então (Then) o navegador deve exibir um alerta de acesso negado
    """
    login_page = LoginPage(page)

    # Dado que o usuário acessa a tela de Login
    login_page.acessar_pagina()

    assert "Bem-vindo ao projeto de" in login_page.titulo.inner_text()

    mensagens_alerta = []
    page.on("dialog", lambda dialog: (mensagens_alerta.append(dialog.message), dialog.accept()))

    # Quando informa credenciais inválidas e submete o formulário
    login_page.preencher_login("usuario_invalido@teste.com", "senha_errada")
    login_page.submeter_formulario()
    page.wait_for_timeout(500)

    # Então o navegador exibe um alerta de acesso negado
    assert mensagens_alerta, "Nenhum alerta foi exibido na tentativa de falha."
    assert "Acesso negado" in mensagens_alerta[0], (
        f"Mensagem incorreta: {mensagens_alerta[0]}"
    )


def test_cadastro_e_login_com_sucesso(page, massa_usuario_dinamico):
    """
    Cenário (BDD): Usuário se cadastra 100% pela UI, faz login e acessa o dashboard.
    """
    login_page = LoginPage(page)
    dashboard_page = DashboardPage(page)

    # Dado que o visitante preenche o formulário de cadastro corretamente
    page.goto(f"{BASE_URL}/cadastro")
    page.locator("#nome").fill(massa_usuario_dinamico["nome"])
    page.locator("#email").fill(massa_usuario_dinamico["email"])
    page.locator("#telefone").fill(massa_usuario_dinamico["telefone"])
    page.locator("#senha").fill(massa_usuario_dinamico["senha"])
    page.once("dialog", lambda dialog: dialog.accept())

    # Quando finaliza o cadastro e entra com as mesmas credenciais
    page.locator('button[type="submit"]').click()

    page.wait_for_url(f"{BASE_URL}/", timeout=5000)
    login_page.preencher_login(
        massa_usuario_dinamico["email"], massa_usuario_dinamico["senha"]
    )
    login_page.submeter_formulario()

    # Então o sistema armazena o token JWT e abre o dashboard
    page.wait_for_url(dashboard_page.url_esperada, timeout=5000)
    page.wait_for_function(
        "() => localStorage.getItem('token') !== null",
        timeout=5000,
    )
    token = page.evaluate("() => localStorage.getItem('token')")
    assert token and token != "undefined", (
        "O token JWT não foi armazenado corretamente no localStorage após o login."
    )

    assert dashboard_page.validar_redirecionamento_com_sucesso(), (
        "O navegador falhou ao redirecionar para a página de dashboard."
    )