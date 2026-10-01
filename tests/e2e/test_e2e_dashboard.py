import uuid

import pytest

from backend.database import conectar_banco


BASE_URL = "http://localhost:5000"


@pytest.fixture
def dados_usuario_dashboard():
    """Gera dados únicos em memória para teste via tela, sem inserir no banco."""
    email_unico = f"dash_ui_{uuid.uuid4().hex[:8]}@fluxocaixa.com"
    dados = {
        "nome": "Usuario Dashboard Teste",
        "email": email_unico,
        "telefone": "(11) 98888-0000",
        # O formulário de login limita a senha a seis caracteres.
        "senha": "123456",
    }

    yield dados

    conexao = conectar_banco()
    try:
        conexao.execute(
            "DELETE FROM transacoes "
            "WHERE usuario_id IN (SELECT id FROM usuarios WHERE email = ?)",
            (email_unico,),
        )
        conexao.execute(
            "DELETE FROM historico_saldos "
            "WHERE usuario_id IN (SELECT id FROM usuarios WHERE email = ?)",
            (email_unico,),
        )
        conexao.execute(
            "DELETE FROM saldos "
            "WHERE usuario_id IN (SELECT id FROM usuarios WHERE email = ?)",
            (email_unico,),
        )
        conexao.execute("DELETE FROM usuarios WHERE email = ?", (email_unico,))
        conexao.commit()
    finally:
        conexao.close()


def test_cadastro_usuario_e_bloqueio_saldo_inicial(page, dados_usuario_dashboard):
    """
    Cenário (BDD): Usuário faz cadastro na UI, acessa o dashboard e define o saldo inicial.
    """
    # Dado que um novo usuário se cadastra e faz login com sucesso
    page.goto(f"{BASE_URL}/cadastro")
    page.locator("#nome").fill(dados_usuario_dashboard["nome"])
    page.locator("#email").fill(dados_usuario_dashboard["email"])
    page.locator("#telefone").fill(dados_usuario_dashboard["telefone"])
    page.locator("#senha").fill(dados_usuario_dashboard["senha"])
    page.once("dialog", lambda dialog: dialog.accept())
    page.locator('button[type="submit"]').click()

    page.wait_for_url(f"{BASE_URL}/", timeout=5000)
    page.locator("input[type='email']").fill(dados_usuario_dashboard["email"])
    page.locator("input[type='password']").fill(dados_usuario_dashboard["senha"])
    page.locator('button[type="submit"]').click()

    # Quando o usuário acessa a rota do dashboard
    page.wait_for_url(f"{BASE_URL}/dashboard", timeout=5000)

    # Então o sistema exibe o modal obrigatório de saldo inicial
    page.wait_for_selector("#modalSaldoInicial", state="visible", timeout=5000)

    # Quando o usuário informa o valor do saldo e salva
    page.locator("#inputNovoSaldo").fill("1500.00")
    page.locator("#btnSalvarSaldo").click()

    # Então o modal fecha e o card de saldo atualizado reflete o valor
    page.wait_for_selector("#modalSaldoInicial", state="hidden", timeout=5000)
    saldo_display = page.locator("#cardSaldoAtual").inner_text()
    assert "1.500,00" in saldo_display, (
        f"Saldo esperado não encontrado. Retornou: {saldo_display}"
    )
