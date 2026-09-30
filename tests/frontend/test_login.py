def test_front_end_tela_login_acessivel(client):
    """
    Cenário (BDD): Usuário acessa o sistema pela primeira vez.
    
    Dado (Given) que o usuário não está autenticado
    Quando (When) ele acessar a raiz da aplicação '/'
    Então (Then) o servidor deve retornar a página HTML (Status 200)
    E (And) o conteúdo deve conter a palavra "Login"
    """
    response = client.get('/')
    
    # Na fase Red do TDD, esperamos que isso quebre com Erro 404 (Not Found),
    # pois o Flask ainda não sabe que o frontend existe.
    assert response.status_code == 200
    assert b"Login" in response.data