import sqlite3
import os

# 1. Restauração da Lógica de Ambiente
ENV = os.getenv('FLASK_ENV', 'development')
if ENV == 'test':
    DB_PATH = 'fluxo_caixa_teste.db'
else:
    DB_PATH = os.getenv('DATABASE_URL', 'app_prd.db')

def obter_conexao():
    """Retorna uma conexão ativa com o banco de dados configurado para o ambiente."""
    conexao = sqlite3.connect(DB_PATH)
    conexao.row_factory = sqlite3.Row
    return conexao

# Alias vital para manter retrocompatibilidade com códigos novos (transacoes.py) e velhos (ocr.py)
conectar_banco = obter_conexao

def inicializar_banco():
    """Inicializa as tabelas oficiais do sistema no banco de dados."""
    conexao = obter_conexao()
    cursor = conexao.cursor()
    
    # Tabela 1: Usuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha_pin TEXT NOT NULL,
            telefone TEXT
        )
    ''')
    
    # Tabela 2: Saldo Inicial
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS saldo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            valor REAL NOT NULL,
            data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
        )
    ''')
    
    # Tabela 3: Lançamentos (Fonte Única da Verdade para Extrato, Transações e OCR)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lancamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            tipo TEXT NOT NULL,
            valor REAL NOT NULL,
            data_lancamento TEXT,
            estabelecimento TEXT,
            categoria TEXT DEFAULT 'Outros',
            data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
        )
    ''')
    
    # Migração segura para não quebrar bancos antigos que não têm a coluna categoria
    try:
        cursor.execute("ALTER TABLE lancamentos ADD COLUMN categoria TEXT DEFAULT 'Outros'")
    except sqlite3.OperationalError:
        pass  # A coluna já existe, segue o jogo
        
    conexao.commit()
    conexao.close()

if __name__ == '__main__':
    inicializar_banco()