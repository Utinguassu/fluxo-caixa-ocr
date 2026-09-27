import os
import pytest
from datetime import datetime
from backend.app import app
from flask_jwt_extended import create_access_token
from backend.database import obter_conexao, inicializar_banco

@pytest.fixture(autouse=True)
def limpar_banco_antes_de_cada_teste():
    """Garante um banco zerado e isolado antes de CADA teste."""
    inicializar_banco()
    conn = obter_conexao()
    conn.execute('DELETE FROM transacoes')
    conn.execute('DELETE FROM usuarios')
    conn.commit()
    conn.close()

@pytest.fixture
def client():
    """Configura o cliente de testes simulando o servidor Flask."""
    app.config['TESTING'] = True
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    with app.test_client() as client:
        yield client

@pytest.fixture
def token():
    """Gera um token JWT real e injeta o usuário base para os testes que exigem login."""
    conn = obter_conexao()
    conn.execute('''
        INSERT INTO usuarios (id, nome, email, senha_pin) 
        VALUES (1, 'Usuario OCR Teste', 'teste@ocr.com', '1234')
    ''')
    conn.commit()
    conn.close()

    with app.app_context():
        return create_access_token(identity=1)

# --- CONFIGURAÇÃO DO RELATÓRIO HTML ---

@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    """Personaliza o nome do relatório HTML com data, hora e ambiente."""
    ambiente = "GitHub" if os.getenv("GITHUB_ACTIONS") == "true" else "Local"
    agora = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    nome_arquivo = f"relatorios/relatorio_{ambiente}_{agora}.html"
    config.option.htmlpath = nome_arquivo

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Substitui o nome técnico do teste pela descrição amigável (Docstring) no relatório."""
    outcome = yield
    report = outcome.get_result()
    docstring = getattr(item.function, '__doc__', None)
    if docstring:
        report.nodeid = docstring.strip()