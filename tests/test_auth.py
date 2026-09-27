def test_cadastro_sucesso(client):
    """Teste 01 - Cadastro: Valida se um novo usuário é criado com sucesso."""
    response = client.post('/cadastro', json={
        'nome': 'Novo Usuario',
        'email': 'novo@teste.com',
        'senha_pin': '1234'
    })
    assert response.status_code in [200, 201]

def test_cadastro_email_duplicado(client):
    """Teste 02 - Regra de Negócio: Impede cadastro de e-mail já existente."""
    client.post('/cadastro', json={
        'nome': 'Usuario Duplicado',
        'email': 'duplicado@teste.com',
        'senha_pin': '1234'
    })
    
    # Tenta cadastrar exatamente o mesmo e-mail (agora sem usar timestamps)
    response = client.post('/cadastro', json={
        'nome': 'Outro Nome',
        'email': 'duplicado@teste.com',
        'senha_pin': '4321'
    })
    assert response.status_code == 400

def test_login_case_insensitive(client):
    """Teste 03 - Login Inteligente: Aceita e-mail independentemente de maiúsculas/minúsculas."""
    client.post('/cadastro', json={
        'nome': 'Usuario Case',
        'email': 'case@teste.com',
        'senha_pin': '1234'
    })
    
    response = client.post('/login', json={
        'email': 'CASE@TESTE.COM',
        'senha_pin': '1234'
    })
    assert response.status_code == 200