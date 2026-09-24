import os
import pytest
from backend.app import app
from backend.database import inicializar_banco

@pytest.fixture
def cliente(tmp_path):
    # Isolamento absoluto para o teste
    db_path = tmp_path / "fluxo_caixa_teste.db"
    os.environ["DB_PATH"] = str(db_path)
    os.environ["JWT_SECRET_KEY"] = "chave-falsa-apenas-para-testes-com-32-bytes"
    
    app.config['TESTING'] = True

    # Cria as tabelas do banco de dados na pasta temporária
    inicializar_banco()

    with app.test_client() as client:
        yield client

def test_isolamento_transacoes_rn07(cliente):
    """Teste TDD: Garante que um utilizador só acede aos seus próprios dados"""
    
    # 1. Cadastra e loga o Usuário A (João)
    cliente.post('/cadastro', json={"nome": "João", "email": "joao@exemplo.com", "senha_pin": "123456"})
    resp_login_joao = cliente.post('/login', json={"email": "joao@exemplo.com", "senha_pin": "123456"})
    token_joao = resp_login_joao.get_json()["token"]

    # 2. Cadastra e loga o Usuário B (Maria)
    cliente.post('/cadastro', json={"nome": "Maria", "email": "maria@exemplo.com", "senha_pin": "654321"})
    resp_login_maria = cliente.post('/login', json={"email": "maria@exemplo.com", "senha_pin": "654321"})
    token_maria = resp_login_maria.get_json()["token"]

    # 3. João cadastra uma despesa (Enviando o seu Token JWT no cabeçalho)
    headers_joao = {"Authorization": f"Bearer {token_joao}"}
    resposta_criacao = cliente.post('/transacoes', json={
        "tipo": "despesa",
        "valor": 150.50,
        "descricao": "Conta de Luz"
    }, headers=headers_joao)
    
    assert resposta_criacao.status_code == 201
    
    # 4. João consulta as suas transações (Deve ver 1 transação)
    resp_get_joao = cliente.get('/transacoes', headers=headers_joao)
    transacoes_joao = resp_get_joao.get_json()
    assert len(transacoes_joao) == 1
    assert transacoes_joao[0]["descricao"] == "Conta de Luz"

    # 5. A PROVA DE FOGO (RN07): Maria consulta as transações dela
    headers_maria = {"Authorization": f"Bearer {token_maria}"}
    resp_get_maria = cliente.get('/transacoes', headers=headers_maria)
    transacoes_maria = resp_get_maria.get_json()
    
    # Maria não pode ver a conta de luz do João! O array dela deve vir vazio.
    assert len(transacoes_maria) == 0