import pytest

def obter_token_teste(client, email):
    """Função auxiliar para criar usuário e retornar token JWT."""
    client.post('/cadastro', json={
        'nome': 'Usuario Teste',
        'email': email,
        'senha_pin': '1234',
        'telefone': '(11) 99999-9999'
    })
    resp = client.post('/login', json={'email': email, 'senha_pin': '1234'})
    dados = resp.get_json() or {}
    return dados.get('access_token') or dados.get('token')

def test_dado_dois_usuarios_quando_um_consulta_extrato_entao_nao_ve_dados_do_outro(client):
    """
    Transações: Segurança e Isolamento (RN07)
    
    Dado (Given) que existem dois usuários (A e B)
    E (And) o Usuário A registra uma despesa
    Quando (When) o Usuário B consultar o seu extrato
    Então (Then) ele não deve ver a transação do Usuário A
    """
    token_a = obter_token_teste(client, "usuario_a@teste.com")
    token_b = obter_token_teste(client, "usuario_b@teste.com")
    
    # Usuário A cria um lançamento
    client.post('/transacoes', json={
        'tipo': 'CARTAO',
        'valor': 500.00,
        'estabelecimento': 'Loja do Usuario A'
    }, headers={'Authorization': f'Bearer {token_a}'})
    
    # Usuário B consulta o PRÓPRIO extrato
    response_b = client.get('/api/extrato', headers={'Authorization': f'Bearer {token_b}'})
    
    assert response_b.status_code == 200
    dados_b = response_b.get_json()
    
    assert dados_b['total_registros'] == 0
    assert len(dados_b['lancamentos']) == 0

def test_dado_varios_lancamentos_quando_consultar_extrato_entao_retorna_ordenado_mais_recente(client):
    """
    Transações: Ordenação Cronológica da Linha do Tempo (RN04)
    
    Dado (Given) que o usuário possui lançamentos cadastrados em datas diferentes
    Quando (When) consultar o extrato
    Então (Then) os itens devem vir ordenados do mais recente para o mais antigo
    """
    token = obter_token_teste(client, "ordem@teste.com")
    headers = {'Authorization': f'Bearer {token}'}
    
    # Registra lançamentos em datas diferentes (Padaria antiga, Mercado recente)
    client.post('/transacoes', json={
        'tipo': 'PIX', 
        'valor': 10.0, 
        'estabelecimento': 'Padaria',
        'data_lancamento': '2026-10-01'
    }, headers=headers)
    
    client.post('/transacoes', json={
        'tipo': 'CARTAO', 
        'valor': 50.0, 
        'estabelecimento': 'Mercado',
        'data_lancamento': '2026-10-15'
    }, headers=headers)
    
    response = client.get('/api/extrato', headers=headers)
    assert response.status_code == 200
    
    dados = response.get_json()
    assert dados['total_registros'] == 2
    
    # O lançamento mais recente (Mercado - 15/10) vem antes do antigo (Padaria - 01/10)
    assert dados['lancamentos'][0]['estabelecimento'] == 'Mercado'
    assert dados['lancamentos'][1]['estabelecimento'] == 'Padaria'