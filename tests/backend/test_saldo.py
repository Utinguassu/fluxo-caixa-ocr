from backend.services.saldo_service import SaldoService

def test_calculo_saldo_com_multiplas_despesas():
    """
    Cenário (BDD): Usuário faz compras e o saldo atual é deduzido corretamente.
    
    Dado (Given) que o usuário tem um saldo inicial de R$ 1000.00
    E (And) possui três transações cadastradas (R$ 100.00, R$ 50.50, R$ 200.00)
    Quando (When) o motor financeiro calcular o saldo atual
    Então (Then) o retorno deve ser exatos R$ 649.50
    """
    # Dado (Setup)
    saldo_inicial = 1000.00
    
    # Simulando o formato das transações que o banco de dados nos entregaria
    transacoes = [
        {"valor": 100.00},
        {"valor": 50.50},
        {"valor": 200.00}
    ]

    # Quando (Ação)
    saldo_atual = SaldoService.calcular(saldo_inicial, transacoes)

    # Então (Garantia da precisão com 2 casas decimais)
    assert saldo_atual == 649.50


def test_calculo_saldo_negativo():
    """
    Cenário (BDD): Usuário gasta mais do que o saldo inicial.
    
    Dado (Given) que o usuário tem saldo inicial nulo (0.00)
    E (And) registra uma despesa de R$ 150.00
    Então (Then) o saldo atual deve ser R$ -150.00
    """
    saldo_atual = SaldoService.calcular(0.00, [{"valor": 150.00}])
    assert saldo_atual == -150.00

def test_api_saldo_atualizado(client, token):
    """
    Cenário (BDD): O front-end solicita o saldo atualizado do usuário logado.
    Quando (When) eu fizer uma requisição GET para a rota /saldo
    Então (Then) a API deve retornar status 200 e o campo 'saldo_atual'
    """
    response = client.get(
        '/saldo',
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Na fase Red do TDD, esperamos que isso quebre com um Erro 404 (Not Found), 
    # pois a rota ainda não foi construída no backend.
    assert response.status_code == 200
    assert "saldo_atual" in response.json    


def test_api_cadastra_e_consulta_saldo_inicial(client, token):
    headers = {"Authorization": f"Bearer {token}"}

    consulta_inicial = client.get('/api/saldo', headers=headers)
    assert consulta_inicial.status_code == 200
    assert consulta_inicial.json == {"precisa_saldo_inicial": True}

    cadastro = client.post('/api/saldo', json={"valor": 850.75}, headers=headers)
    assert cadastro.status_code == 201

    consulta_final = client.get('/api/saldo', headers=headers)
    assert consulta_final.status_code == 200
    assert consulta_final.json == {
        "precisa_saldo_inicial": False,
        "saldo_inicial": 850.75,
        "total_debitos": 0.0,
        "saldo_atualizado": 850.75,
    }


def test_api_cadastro_saldo_exige_valor(client, token):
    response = client.post(
        '/api/saldo',
        json={},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 400
    assert response.json == {"erro": "Valor é obrigatório"}