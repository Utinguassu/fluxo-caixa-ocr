import uuid
import pytest
from backend.database import conectar_banco
from tests.e2e.pages.dashboard_page import DashboardPage
from tests.e2e.pages.login_page import LoginPage

BASE_URL = "http://localhost:5000"

@pytest.fixture
def massa_usuario_dinamico():
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
            "DELETE FROM lancamentos "
            "WHERE usuario_id IN (SELECT id FROM usuarios WHERE email = ?)",
            (dados["email"],),
        )
        conexao.execute("DELETE FROM usuarios WHERE email = ?", (dados["email"],))
        conexao.commit()
    finally:
        conexao.close()

def test_login_interface_e_falha(page):
    login_page = LoginPage(page)
    login_page.acessar_pagina()

    assert "Bem-vindo ao projeto de" in login_page.titulo.inner_text()

    mensagens_alerta = []
    page.on("dialog", lambda dialog: (mensagens_alerta.append(dialog.message), dialog.accept()))

    login_page.preencher_login("usuario_invalido@teste.com", "senha_errada")
    login_page.submeter_formulario()
    page.wait_for_timeout(500)

    assert mensagens_alerta, "Nenhum alerta foi exibido na tentativa de falha."
    assert "Acesso negado" in mensagens_alerta[0], (
        f"Mensagem incorreta: {mensagens_alerta[0]}"
    )

def test_cadastro_e_login_com_sucesso(page, massa_usuario_dinamico):
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