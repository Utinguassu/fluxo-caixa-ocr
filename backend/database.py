import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PRD_PATH = os.path.join(BASE_DIR, 'db', 'prd', 'app_prd.db')
DB_TEST_PATH = os.path.join(BASE_DIR, 'db', 'tests', 'manual_test.db')

def conectar_banco(ambiente=None):
    """
    Gere a conexão com o banco de dados de acordo com o ambiente:
    - 'prd': Banco de dados oficial da aplicação.
    - 'test': Banco de dados isolado para testes manuais/automatizados.
    """
    os.makedirs(os.path.dirname(DB_PRD_PATH), exist_ok=True)
    os.makedirs(os.path.dirname(DB_TEST_PATH), exist_ok=True)

    env = ambiente or os.getenv("FLASK_ENV", "prd")
    caminho_db = DB_TEST_PATH if env == "test" else DB_PRD_PATH

    # Mantem DB_PATH como override para os testes temporarios ja existentes.
    if ambiente is None:
        caminho_db = os.getenv("DB_PATH", caminho_db)

    conn = sqlite3.connect(caminho_db)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn

def inicializar_banco(ambiente=None):
    conexao = conectar_banco(ambiente)
    cursor = conexao.cursor()
    
    # Tabela de Usuários (CARD-01)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha_pin TEXT NOT NULL
        )
    ''')
    
    # NOVA: Tabela de Histórico de Saldos Iniciais (RN05 e RN05.01)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historico_saldos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            valor REAL NOT NULL,
            data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS saldos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            valor REAL NOT NULL,
            data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
        )
    ''')
    
    # Tabela de Transações com Isolamento por Usuário (CARD-02)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            tipo TEXT NOT NULL, 
            valor REAL NOT NULL,
            descricao TEXT NOT NULL,
            data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            categoria TEXT DEFAULT 'Outros',
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        )
    ''')

# Tabela para armazenar os débitos capturados (RN01, RN02, RN03)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lancamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            tipo TEXT NOT NULL, -- 'PIX/CC' ou 'CARTAO'
            valor REAL NOT NULL,
            data_lancamento DATE,
            estabelecimento TEXT,
            data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
        )
    ''')
    
    cursor.execute('PRAGMA table_info(transacoes)')
    colunas_transacoes = {coluna['name'] for coluna in cursor.fetchall()}
    if 'categoria' not in colunas_transacoes:
        cursor.execute("ALTER TABLE transacoes ADD COLUMN categoria TEXT DEFAULT 'Outros'")
    
    conexao.commit()
    conexao.close()


# Alias para manter compatibilidade com modulos que usam obter_conexao().
obter_conexao = conectar_banco

# Permite executar o script diretamente no terminal para criar/atualizar o banco
if __name__ == '__main__':
    inicializar_banco()
    print("Banco de dados inicializado/atualizado com sucesso!")