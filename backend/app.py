import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from flasgger import Swagger
import sqlite3

app = Flask(__name__)
CORS(app)
Swagger(app) # Ativa o painel visual do Swagger em /apidocs

PASTA_BACKEND = os.path.dirname(os.path.abspath(__file__))
BANCO_PADRAO = os.path.join(PASTA_BACKEND, "fluxo_caixa.db")

def conectar_banco():
    """Lê a variável de ambiente dinamicamente a cada chamada (suporta testes isolados)"""
    caminho_ativo = os.getenv("DB_PATH", BANCO_PADRAO)
    return sqlite3.connect(caminho_ativo)

def inicializar_banco():
    """Garante que a tabela existe no banco de dados ativo"""
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

# Inicializa as tabelas no banco padrão de produção ao arrancar a aplicação
inicializar_banco()

# ---------------------------------------------------------
# ROTA 1: CADASTRO DE UTILIZADOR
# ---------------------------------------------------------
@app.route('/cadastro', methods=['POST'])
def cadastrar_usuario():
    """
    Registo de novo utilizador no sistema
    ---
    tags:
      - Autenticação
    parameters:
      - name: corpo
        in: body
        required: true
        schema:
          type: object
          properties:
            nome:
              type: string
              example: "Utinguassu Barbosa"
            email:
              type: string
              example: "tinga@exemplo.com"
            senha_pin:
              type: string
              example: "123456"
    responses:
      201:
        description: Utilizador cadastrado com sucesso!
      400:
        description: Erro de validação ou e-mail já existente.
    """
    dados = request.get_json() or {}
    nome = dados.get('nome')
    email_bruto = dados.get('email')
    senha_pin = dados.get('senha_pin')

    if not nome or not email_bruto or not senha_pin:
        return jsonify({"erro": "Todos os campos são obrigatórios!"}), 400

    email_formatado = email_bruto.strip().lower()

    try:
        conexao = conectar_banco()
        cursor = conexao.cursor()
        cursor.execute("INSERT INTO usuarios (nome, email, senha_pin) VALUES (?, ?, ?)", (nome, email_formatado, senha_pin))
        conexao.commit()
        conexao.close()
        return jsonify({"mensagem": "Usuário cadastrado com sucesso!"}), 201
    
    except sqlite3.IntegrityError:
        return jsonify({"erro": "Este e-mail já está cadastrado."}), 400

# ---------------------------------------------------------
# ROTA 2: LOGIN DE UTILIZADOR
# ---------------------------------------------------------
@app.route('/login', methods=['POST'])
def login():
    """
    Autenticação de utilizador (Login)
    ---
    tags:
      - Autenticação
    parameters:
      - name: corpo
        in: body
        required: true
        schema:
          type: object
          properties:
            email:
              type: string
              example: "tinga@exemplo.com"
            senha_pin:
              type: string
              example: "123456"
    responses:
      200:
        description: Login aprovado com sucesso.
      401:
        description: E-mail ou PIN incorretos.
      400:
        description: Campos obrigatórios em falta.
    """
    dados = request.get_json() or {}
    email_bruto = dados.get('email')
    senha_pin = dados.get('senha_pin')

    if not email_bruto or not senha_pin:
        return jsonify({"erro": "E-mail e senha são obrigatórios!"}), 400

    email_formatado = email_bruto.strip().lower()

    conexao = conectar_banco()
    cursor = conexao.cursor()
    cursor.execute("SELECT id, nome FROM usuarios WHERE email = ? AND senha_pin = ?", (email_formatado, senha_pin))
    usuario = cursor.fetchone()
    conexao.close()

    if usuario:
        return jsonify({"mensagem": "Login aprovado", "usuario_id": usuario[0], "nome": usuario[1]}), 200
    else:
        return jsonify({"erro": "E-mail ou PIN incorretos."}), 401

if __name__ == '__main__':
    print("🚀 API com Swagger ligada em http://localhost:5000/apidocs")
    app.run(host='0.0.0.0', port=5000, debug=True)