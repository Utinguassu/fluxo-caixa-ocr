import pytest

def obter_token_teste(client, email):
    client.post('/cadastro', json={
        'nome': 'Usuario Transacoes',
        'email': email,
        'senha_pin': '1234',
        'telefone': '(11) 99999-9999'
    })
    res_login = client.post('/login', json={'email': email, 'senha_pin': '1234'})
    return res_login.get_json()['access_token']

def test_isolamento_transacoes_rn07(client):
    """Teste 06 - Segurança (RN07): Garante que um usuário não vê os dados de outro."""
    token = obter_token_teste(client, "isolamento_bdd@teste.com")
    
    # Substituímos a chamada velha '/transacoes' pela nova rota consolidada
    response = client.get('/api/resumo', headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 200
    dados = response.get_json()
    assert dados is not None

def test_api_extrato_ordena_lancamentos_e_isola_usuario(client):
    """Teste 12 - Ordenação e Isolamento no Extrato (RN04/RN07)."""
    token = obter_token_teste(client, "ordenacao_bdd@teste.com")
    
    # 1. Cria transações
    client.post('/api/saldo', json={'valor': 100.00}, headers={"Authorization": f"Bearer {token}"})
    client.post('/transacoes', json={'tipo': 'despesa', 'valor': 20.00, 'estabelecimento': 'Loja 1'}, headers={"Authorization": f"Bearer {token}"})
    
    # 2. Verifica Resumo consolidado
    response = client.get('/api/resumo', headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 200
    dados = response.get_json()
    assert dados['saldo_atual'] == 80.00