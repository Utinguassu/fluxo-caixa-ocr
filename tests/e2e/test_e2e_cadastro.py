from uuid import uuid4

import pytest

from backend.database import conectar_banco


BASE_URL = "http://localhost:5000"


@pytest.fixture
def dados_usuario_cadastro():
    email = f"cadastro_e2e_{uuid4().hex}@fluxocaixa.com"
    usuario = {
        "nome": "Usuario Cadastro E2E",
        "email": email,
        "telefone": "(11) 99999-9999",
        "senha": "123456",
    }

    yield usuario

    conexao = conectar_banco()
    try:
        conexao.execute(
            "DELETE FROM transacoes "
            "WHERE usuario_id IN (SELECT id FROM usuarios WHERE email = ?)",
            (email,),
        )
        conexao.execute(
            "DELETE FROM historico_saldos "
            "WHERE usuario_id IN (SELECT id FROM usuarios WHERE email = ?)",
            (email,),
        )
        conexao.execute("DELETE FROM usuarios WHERE email = ?", (email,))
        conexao.commit()
    finally:
        conexao.close()


def test_cadastro_pela_interface_salva_telefone(page, dados_usuario_cadastro):
    mensagens_alerta = []
    page.on("dialog", lambda dialog: (mensagens_alerta.append(dialog.message), dialog.accept()))
    page.goto(f"{BASE_URL}/cadastro")

    page.locator("#nome").fill(dados_usuario_cadastro["nome"])
    page.locator("#email").fill(dados_usuario_cadastro["email"])
    page.locator("#telefone").fill(dados_usuario_cadastro["telefone"])
    page.locator("#senha").fill(dados_usuario_cadastro["senha"])
    page.locator('#formCadastro button[type="submit"]').click()

    page.wait_for_url(f"{BASE_URL}/", timeout=5000)
    assert mensagens_alerta == [
        "Cadastro realizado com sucesso! Você será redirecionado para o login."
    ]

    conexao = conectar_banco()
    try:
        usuario = conexao.execute(
            "SELECT telefone FROM usuarios WHERE email = ?",
            (dados_usuario_cadastro["email"],),
        ).fetchone()
    finally:
        conexao.close()

    assert usuario is not None
    assert usuario["telefone"] == dados_usuario_cadastro["telefone"]
