def test_front_end_tela_login_acessivel(client):
    """
    Cenário (BDD): Usuário acessa o sistema pela primeira vez.
    
    Dado (Given) que o usuário não está autenticado
    Quando (When) ele acessar a raiz da aplicação '/'
    Então (Then) o servidor deve retornar a página HTML (Status 200)
    E (And) o conteúdo deve conter a mensagem de boas-vindas "Bem-vindo ao projeto"
    """
    response = client.get('/')
    
    assert response.status_code == 200
    # Valida se a interface atual (Opção 3 - Glassmorphism) foi carregada corretamente
    assert b"Bem-vindo ao projeto" in response.data