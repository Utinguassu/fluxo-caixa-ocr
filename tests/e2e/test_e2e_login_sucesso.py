from uuid import uuid4

import pytest
import requests

from backend.database import conectar_banco
from tests.e2e.pages.dashboard_page import DashboardPage
from tests.e2e.pages.login_page import LoginPage


BASE_URL_API = "http://localhost:5000"


@pytest.fixture
def massa_usuario_dinamico():
    """Cria um usuário válido pela API e remove seus dados ao finalizar o teste."""
    email_teste = f"teste_e2e_{uuid4().hex}@fluxocaixa.com"
    senha_teste = "123456"
    payload = {
        "nome": "Usuario E2E",
        "email": email_teste,
        "senha_pin": senha_teste,
    }

    try:
        response_cadastro = requests.post(
            f"{BASE_URL_API}/cadastro",
            json=payload,
            timeout=10,
        )
        assert response_cadastro.status_code == 201, (
            "Falha ao cadastrar usuário E2E: "
            f"HTTP {response_cadastro.status_code} - {response_cadastro.text}"
        )

        yield {"email": email_teste, "senha": senha_teste}
    finally:
        conexao = conectar_banco()
        try:
            conexao.execute(
                "DELETE FROM transacoes "
                "WHERE usuario_id IN (SELECT id FROM usuarios WHERE email = ?)",
                (email_teste,),
            )
            conexao.execute(
                "DELETE FROM historico_saldos "
                "WHERE usuario_id IN (SELECT id FROM usuarios WHERE email = ?)",
                (email_teste,),
            )
            conexao.execute("DELETE FROM usuarios WHERE email = ?", (email_teste,))
            conexao.commit()
        finally:
            conexao.close()


def test_login_com_sucesso_e_redirecionamento(page, massa_usuario_dinamico):
    """
    Cenário (BDD): Usuário realiza login com credenciais válidas e acessa o dashboard.

    Dado (Given) que o usuário possui um cadastro válido na base de dados
    E (And) acessa a tela de login do sistema
    Quando (When) ele preenche seu e-mail e senha corretos
    E (And) clica no botão 'Acessar Sistema'
    Então (Then) o navegador deve armazenar o token JWT no localStorage
    E (And) o usuário deve ser redirecionado com sucesso para a rota '/dashboard'
    """
    login_page = LoginPage(page)
    dashboard_page = DashboardPage(page)

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

    sucesso_redirecionamento = dashboard_page.validar_redirecionamento_com_sucesso()
    assert sucesso_redirecionamento, (
        "O navegador falhou ao redirecionar para a página de dashboard."
    )