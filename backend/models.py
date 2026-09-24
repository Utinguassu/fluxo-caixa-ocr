import sqlite3
import os

# 1. Definimos onde o ficheiro do banco de dados vai ser guardado (dentro da pasta backend)
PASTA_BACKEND = os.path.dirname(os.path.abspath(__file__))
CAMINHO_BANCO = os.path.join(PASTA_BACKEND, "fluxo_caixa.db")

def criar_banco_de_dados():
    # 2. Criamos a ligação. Se o ficheiro 'fluxo_caixa.db' não existir, o Python cria-o magicamente!
    conexao = sqlite3.connect(CAMINHO_BANCO)
    cursor = conexao.cursor()

    # 3. Criamos a Tabela de Utilizadores (Atendendo à Regra de Negócio RN06 e RN08)
    # Usamos TEXT para a senha para evitar que um PIN começado por zero perca esse zero (ex: 012345)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha_pin TEXT NOT NULL
        )
    ''')

    # 4. Guardamos as alterações e fechamos a porta do banco de dados
    conexao.commit()
    conexao.close()
    
    print("✅ Sucesso! Banco de dados 'fluxo_caixa.db' e tabela de utilizadores criados e prontos a usar.")

# 5. Esta linha diz ao Python para executar a função acima assim que rodarmos este ficheiro
if __name__ == "__main__":
    criar_banco_de_dados()