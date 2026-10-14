import pytest

def obter_token_teste(client, email):
    client.post('/cadastro', json={
        'nome': 'Usuario Saldo',
        'email': email,
        'senha_pin': '1234',
        'telefone': '(11) 99999-9999'
    })
    resp = client.post('/login', json={'email': email, 'senha_pin': '1234'})
    dados = resp.get_json() or {}
    return dados.get('access_token') or dados.get('token')

def test_dado_usuario_novo_quando_cadastrar_saldo_entao_salva_com_sucesso(client):
    token = obter_token_teste(client, "saldo_novo_bdd@teste.com")
    headers = {'Authorization': f'Bearer {token}'}
    
    response = client.post('/api/saldo', json={'valor': 1500.00}, headers=headers)
    dados = response.get_json() or {}
    
    assert response.status_code == 201
    assert "mensagem" in dados or "sucesso" in str(dados).lower() or dados.get("status") in ["success", "sucesso"]

def test_dado_usuario_com_saldo_e_despesas_quando_consultar_entao_retorna_calculo_correto(client):
    token = obter_token_teste(client, "saldo_calculo_bdd@teste.com")
    headers = {'Authorization': f'Bearer {token}'}
    
    # 1. Define Saldo Inicial
    res_saldo = client.post('/api/saldo', json={'valor': 1000.00}, headers=headers)
    assert res_saldo.status_code == 201
    
    # 2. Registra Débito via API (Sem campo descricao)
    res_trans = client.post('/transacoes', json={
        'tipo': 'CARTAO',
        'valor': 150.00,
        'estabelecimento': 'Mercado Central'
    }, headers=headers)
    assert res_trans.status_code == 201
    
    # 3. Consulta o saldo consolidado
    response = client.get('/api/saldo', headers=headers)
    dados = response.get_json() or {}
    
    assert response.status_code == 200
    assert dados['saldo_inicial'] == 1000.00
    assert dados['total_debitos'] == 150.00
    assert dados['saldo_atualizado'] == 850.00

def test_dado_payload_invalido_quando_cadastrar_saldo_entao_retorna_erro_400(client):
    token = obter_token_teste(client, "saldo_erro_bdd@teste.com")
    headers = {'Authorization': f'Bearer {token}'}
    
    response = client.post('/api/saldo', json={}, headers=headers)
    assert response.status_code == 400