import os
import pytest

# ISOLAMENTO TOTAL PARA TESTES:
os.environ["DB_PATH"] = ":memory:" # ou o caminho do tmp_path
os.environ["JWT_SECRET_KEY"] = "chave-falsa-apenas-para-testes-com-32-bytes" # <--- Adicione esta linha!

from backend.app import app
from backend.database import conectar_banco

# ... resto do código

@pytest.fixture
def cliente(tmp_path):
    # Cria um banco de dados totalmente isolado e exclusivo para cada teste individual
    db_path = tmp_path / "fluxo_caixa_teste.db"
    os.environ["DB_PATH"] = str(db_path)

    app.config['TESTING'] = True

    # Cria a tabela de usuários neste banco temporário
    conexao = conectar_banco()
    cursor = conexao.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha_pin TEXT NOT NULL
        )
    ''')
    conexao.commit()
    conexao.close()

    with app.test_client() as client:
        yield client

# --- SUÍTE DE TESTES ---

def test_cadastro_sucesso(cliente):
    """Teste Positivo: Registo bem-sucedido de um novo utilizador"""
    resposta = cliente.post('/cadastro', json={
        "nome": "Utinguassu Barbosa",
        "email": "tingateste@exemplo.com",
        "senha_pin": "123456"
    })
    assert resposta.status_code == 201
    assert resposta.get_json()["mensagem"] == "Usuário cadastrado com sucesso!"

def test_cadastro_email_duplicado(cliente):
    """Teste Negativo: Bloqueio de e-mail duplicado (RN06)"""
    payload = {
        "nome": "Utinguassu Barbosa",
        "email": "duplicado@exemplo.com",
        "senha_pin": "123456"
    }
    cliente.post('/cadastro', json=payload)
    resposta = cliente.post('/cadastro', json=payload)
    assert resposta.status_code == 400
    assert "já está cadastrado" in resposta.get_json()["erro"]

def test_login_case_insensitive(cliente):
    """Teste de Regra de Negócio: Registo em maiúsculas e login em minúsculas"""
    cliente.post('/cadastro', json={
        "nome": "Utinguassu Barbosa",
        "email": "TingaTESTE@Exemplo.com",
        "senha_pin": "9876"
    })
    
    resposta = cliente.post('/login', json={
        "email": "tingateste@exemplo.com",
        "senha_pin": "9876"
    })
    assert resposta.status_code == 200
    assert resposta.get_json()["mensagem"] == "Login aprovado"