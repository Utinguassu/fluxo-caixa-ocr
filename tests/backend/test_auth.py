import pytest

def test_dado_usuario_valido_quando_enviar_dados_entao_cadastra_com_sucesso(client):
    """
    API Auth: Cadastro de utilizador com sucesso
    
    Dado (Given) dados de usuário corretos e e-mail inédito
    Quando (When) disparar POST para /cadastro
    Então (Then) retorna 201 e a mensagem de sucesso
    """
    response = client.post('/cadastro', json={
        'nome': 'Novo Usuario BDD',
        'email': 'novo_bdd@teste.com',
        'senha_pin': '1234',
        'telefone': '(11) 99999-9999'
    })
    
    assert response.status_code == 201
    assert "sucesso" in response.get_json().get("mensagem", "").lower()

def test_dado_email_existente_quando_cadastrar_entao_retorna_erro_de_duplicidade(client):
    """
    API Auth: Impede e-mails duplicados
    
    Dado (Given) que o e-mail já existe no banco
    Quando (When) tentar cadastrar um novo usuário com o mesmo e-mail
    Então (Then) retorna status 400 com erro de duplicidade
    """
    # 1. Cadastro Inicial
    client.post('/cadastro', json={
        'nome': 'Usuario Original',
        'email': 'duplicado_bdd@teste.com',
        'senha_pin': '1234',
        'telefone': '(11) 99999-9999'
    })
    
    # 2. Tentativa de Duplicação
    response = client.post('/cadastro', json={
        'nome': 'Usuario Clone',
        'email': 'duplicado_bdd@teste.com',
        'senha_pin': '4321',
        'telefone': '(11) 88888-8888'
    })
    
    assert response.status_code == 400
    assert "erro" in response.get_json()

def test_dado_email_com_maiusculas_quando_fizer_login_entao_aceita_normalmente(client):
    """
    API Auth: Login Inteligente (Case Insensitive)
    
    Dado (Given) um e-mail previamente cadastrado
    Quando (When) tentar fazer login digitando letras maiúsculas
    Então (Then) a API normaliza, autoriza o acesso e retorna o token JWT
    """
    # 1. Cadastro do usuário em minúsculas
    client.post('/cadastro', json={
        'nome': 'Usuario Case BDD',
        'email': 'case_bdd@teste.com',
        'senha_pin': '1234',
        'telefone': '(11) 99999-9999'
    })
    
    # 2. Login com e-mail todo em maiúsculas
    response = client.post('/login', json={
        'email': 'CASE_BDD@TESTE.COM',
        'senha_pin': '1234'
    })
    
    assert response.status_code == 200
    dados = response.get_json()
    assert "access_token" in dados or "token" in dados