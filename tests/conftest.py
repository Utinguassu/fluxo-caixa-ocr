import os
import gc
import pytest
from datetime import datetime
from backend.app import app
from flask_jwt_extended import create_access_token
from backend.database import obter_conexao, inicializar_banco

# Constante isolada exclusiva para o ciclo de testes automatizados (Padrão de Mercado)
JWT_SECRET_KEY_TESTE = "test-secret-key-environment-isolated-2026"

@pytest.fixture(autouse=True)
def limpar_banco_antes_de_cada_teste():
    """Garante um banco zerado e isolado antes de CADA teste (Test Isolation)."""
    gc.collect()
    inicializar_banco()
    conn = obter_conexao()
    conn.execute('DELETE FROM transacoes')
    conn.execute('DELETE FROM saldos')
    conn.execute('DELETE FROM historico_saldos')
    conn.execute('DELETE FROM usuarios')
    conn.commit()
    conn.close()

@pytest.fixture
def client():
    """Configura o Flask Client em modo de teste com chave de mock isolada."""
    app.config['TESTING'] = True
    app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY_TESTE
    with app.test_client() as client:
        yield client

@pytest.fixture
def token(client):
    """Gera um token JWT válido assinado com a mesma chave de mock do ambiente de teste."""
    conn = obter_conexao()
    conn.execute('''
        INSERT INTO usuarios (id, nome, email, senha_pin) 
        VALUES (1, 'Usuario OCR Teste', 'teste@ocr.com', '1234')
    ''')
    conn.commit()
    conn.close()

    app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY_TESTE
    with app.app_context():
        return create_access_token(identity=str(1))

# --- CONFIGURAÇÃO DO RELATÓRIO HTML ---

@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    """Personaliza o nome dinâmico do relatório HTML com base no ambiente (Local vs CI/CD)."""
    ambiente = "GitHub" if os.getenv("GITHUB_ACTIONS") == "true" else "Local"
    agora = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    nome_arquivo = f"relatorios/relatorio_{ambiente}_{agora}.html"
    config.option.htmlpath = nome_arquivo

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Mapeia o nome técnico do teste para a sua descrição de negócio (Docstring) no relatório."""
    outcome = yield
    report = outcome.get_result()
    docstring = getattr(item.function, '__doc__', None)
    if docstring:
        report.nodeid = docstring.strip()