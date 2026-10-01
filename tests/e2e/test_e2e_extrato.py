import os
import re
import uuid

import pytest
from playwright.sync_api import Page, expect

from backend.database import conectar_banco


BASE_URL = os.getenv("E2E_BASE_URL", "http://localhost:5000")


@pytest.fixture
def dados_usuario_dashboard():
    """Gera dados únicos para o fluxo de cadastro pela UI, sem inserir no banco."""
    email_unico = f"extrato_ui_{uuid.uuid4().hex[:8]}@fluxocaixa.com"
    dados = {
        "nome": "Usuario Teste Extrato",
        "email": email_unico,
        "telefone": "(11) 98888-0000",
        # A tela de login limita a senha a seis caracteres.
        "senha": "123456",
    }

    yield dados

    conexao = conectar_banco()
    try:
        for tabela in ("lancamentos", "saldos", "historico_saldos", "transacoes"):
            conexao.execute(
                f"DELETE FROM {tabela} "
                "WHERE usuario_id IN (SELECT id FROM usuarios WHERE email = ?)",
                (email_unico,),
            )
        conexao.execute("DELETE FROM usuarios WHERE email = ?", (email_unico,))
        conexao.commit()
    finally:
        conexao.close()


def test_extrato_cenarios_bdd(page: Page, dados_usuario_dashboard):
    """
    Feature: Linha do Tempo / Extrato (RN04)
    Como um utilizador do sistema
    Quero ver meus débitos organizados de forma cronológica
    Para acompanhar os meus gastos com clareza
    """
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
    page.wait_for_url(f"{BASE_URL}/dashboard", timeout=5000)

    page.wait_for_selector("#modalSaldoInicial", state="visible", timeout=5000)
    page.locator("#inputNovoSaldo").fill("5000.00")
    page.locator("#btnSalvarSaldo").click()
    page.wait_for_selector("#modalSaldoInicial", state="hidden", timeout=5000)

    extrato_container = page.locator("#listaExtrato")
    expect(extrato_container).to_contain_text("Nenhum lançamento registado")

    conexao = conectar_banco()
    try:
        resultado = conexao.execute(
            "SELECT id FROM usuarios WHERE email = ?",
            (dados_usuario_dashboard["email"],),
        ).fetchone()
        assert resultado is not None, "O usuário criado pela interface não foi encontrado."
        usuario_id = resultado["id"]

        conexao.executemany(
            """
            INSERT INTO lancamentos
                (usuario_id, tipo, valor, estabelecimento, data_lancamento)
            VALUES (?, ?, ?, ?, ?)
            """,
            [
                (usuario_id, "CARTAO", 150.50, "Mercado Central", "2026-10-01"),
                (usuario_id, "PIX", 45.00, "Padaria Doce Pão", "2026-10-15"),
            ],
        )
        conexao.commit()
    finally:
        conexao.close()

    page.reload()

    itens_extrato = page.locator("#listaExtrato > div")
    expect(itens_extrato).to_have_count(2)

    primeiro_item = itens_extrato.nth(0)
    segundo_item = itens_extrato.nth(1)

    expect(primeiro_item).to_contain_text("Padaria Doce Pão")
    expect(primeiro_item).to_contain_text("PIX")
    expect(primeiro_item).to_contain_text(re.compile(r"-\s*R\$\s*45,00"))

    expect(segundo_item).to_contain_text("Mercado Central")
    expect(segundo_item).to_contain_text("CARTAO")
    expect(segundo_item).to_contain_text(re.compile(r"-\s*R\$\s*150,50"))
