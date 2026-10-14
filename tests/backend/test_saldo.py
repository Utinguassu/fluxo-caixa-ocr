import pytest
from backend.database import conectar_banco


@pytest.fixture
def header_auth_valido(token):
    return {"Authorization": f"Bearer {token}"}


def test_dado_usuario_novo_quando_consultar_saldo_entao_retorna_precisa_saldo_inicial(client, header_auth_valido):
    """
    Simula o momento em que um usuário acabou de se cadastrar e entra no Dashboard.
    O sistema DEVE informar que ele precisa cadastrar o saldo (Modal Obrigatório).
    """
    resposta = client.get("/api/saldo", headers=header_auth_valido)
    
    assert resposta.status_code == 200
    dados = resposta.get_json()
    assert dados.get("precisa_saldo_inicial") is True


def test_dado_usuario_novo_quando_cadastrar_saldo_entao_salva_com_sucesso(client, header_auth_valido):
    payload = {"valor": 1500.00}
    resposta = client.post("/api/saldo", json=payload, headers=header_auth_valido)
    
    assert resposta.status_code == 201
    assert resposta.get_json()["mensagem"] == "Saldo cadastrado com sucesso!"


def test_dado_usuario_com_saldo_e_despesas_quando_consultar_entao_retorna_calculo_correto(client, header_auth_valido):
    # 1. O usuário cadastra o saldo inicial
    client.post("/api/saldo", json={"valor": 2000.00}, headers=header_auth_valido)
    
    # 2. Inserimos uma despesa na tabela unificada de lançamentos (Mockando o banco)
    conexao = conectar_banco()
    try:
        usuario = conexao.execute("SELECT id FROM usuarios LIMIT 1").fetchone()
        usuario_id = usuario["id"]
        
        conexao.execute(
            "INSERT INTO lancamentos (usuario_id, tipo, valor, estabelecimento, data_lancamento) VALUES (?, ?, ?, ?, ?)",
            (usuario_id, "CARTAO", 500.00, "Mercado Teste", "2026-10-15")
        )
        conexao.commit()
    finally:
        conexao.close()

    # 3. Consultamos o Saldo e verificamos a matemática!
    resposta = client.get("/api/saldo", headers=header_auth_valido)
    
    assert resposta.status_code == 200
    dados = resposta.get_json()
    
    assert dados.get("precisa_saldo_inicial") is False
    assert dados["saldo_inicial"] == 2000.00
    assert dados["total_debitos"] == 500.00
    assert dados["saldo_atualizado"] == 1500.00


def test_dado_payload_invalido_quando_cadastrar_saldo_entao_retorna_erro_400(client, header_auth_valido):
    # Cadastrando sem o campo "valor"
    resposta = client.post("/api/saldo", json={"errado": 100}, headers=header_auth_valido)
    
    assert resposta.status_code == 400
    assert "obrigatório" in resposta.get_json()["erro"].lower()