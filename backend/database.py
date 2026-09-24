import os
import sqlite3

PASTA_BACKEND = os.path.dirname(os.path.abspath(__file__))
BANCO_PADRAO = os.path.join(PASTA_BACKEND, "fluxo_caixa.db")

def conectar_banco():
    caminho_ativo = os.getenv("DB_PATH", BANCO_PADRAO)
    return sqlite3.connect(caminho_ativo)

def inicializar_banco():
    conexao = conectar_banco()
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
    
    # Tabela de Transações com Isolamento por Usuário (CARD-02)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            tipo TEXT NOT NULL, 
            valor REAL NOT NULL,
            descricao TEXT NOT NULL,
            data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        )
    ''')
    
    conexao.commit()
    conexao.close()