import uuid

import pytest

from backend.database import conectar_banco
from tests.e2e.pages.dashboard_page import DashboardPage
from tests.e2e.pages.login_page import LoginPage


BASE_URL = "http://localhost:5000"


@pytest.fixture
def massa_usuario_dinamico():
    """Gera dados únicos para o fluxo de cadastro pela interface."""
    codigo_unico = uuid.uuid4().hex[:8]
    dados = {
        "nome": "Usuario Teste UI",
        "email": f"teste_ui_{codigo_unico}@fluxocaixa.com",
        "telefone": "(11) 98888-7777",
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

    # 1. Dado (Acessa a página)
    login_page.acessar_pagina()

    # 2. E (Valida se o texto da tela está visível)
    assert "Bem-vindo ao projeto de" in login_page.titulo.inner_text()

    # Intercepta e aceita o alerta nativo do navegador
    mensagens_alerta = []
    page.on("dialog", lambda dialog: (mensagens_alerta.append(dialog.message), dialog.accept()))

    # 3. Quando (Preenche os dados falsos)
    login_page.preencher_login("usuario_falso@teste.com", "000000")

    # 4. E (Clica no botão)
    login_page.submeter_formulario()
    page.wait_for_timeout(500)

    # 5. Então (Valida se o alerta de erro apareceu)
    assert len(mensagens_alerta) > 0
    assert "Acesso negado" in mensagens_alerta[0]


def test_cadastro_e_login_com_sucesso(page, massa_usuario_dinamico):
    """
    Cenário (BDD): Usuário se cadastra pela interface, faz login e acessa o dashboard.
    """
    login_page = LoginPage(page)
    dashboard_page = DashboardPage(page)

    page.goto(f"{BASE_URL}/cadastro")
    page.locator("#nome").fill(massa_usuario_dinamico["nome"])
    page.locator("#email").fill(massa_usuario_dinamico["email"])
    page.locator("#telefone").fill(massa_usuario_dinamico["telefone"])
    page.locator("#senha").fill(massa_usuario_dinamico["senha"])
    page.once("dialog", lambda dialog: dialog.accept())
    page.locator('button[type="submit"]').click()

    page.wait_for_url(f"{BASE_URL}/", timeout=5000)
    login_page.acessar_pagina()
    login_page.preencher_login(
        massa_usuario_dinamico["email"], massa_usuario_dinamico["senha"]
    )
    login_page.submeter_formulario()

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