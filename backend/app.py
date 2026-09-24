from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)

PASTA_BACKEND = os.path.dirname(os.path.abspath(__file__))
CAMINHO_BANCO = os.path.join(PASTA_BACKEND, "fluxo_caixa.db")

def conectar_banco():
    return sqlite3.connect(CAMINHO_BANCO)

# ---------------------------------------------------------
# ROTA 1: CADASTRO DE USUÁRIO (CARD-01 / RN06 e RN08)
# ---------------------------------------------------------
@app.route('/cadastro', methods=['POST'])
def cadastrar_usuario():
    dados = request.get_json()
    nome = dados.get('nome')
    email_bruto = dados.get('email')
    senha_pin = dados.get('senha_pin')

    # Validação simples de segurança
    if not nome or not email_bruto or not senha_pin:
        return jsonify({"erro": "Todos os campos são obrigatórios!"}), 400

    # AJUSTE: Remove espaços acidentais e transforma tudo em minúsculas
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
# ROTA 2: LOGIN DE USUÁRIO (CARD-01 / RN06)
# ---------------------------------------------------------
@app.route('/login', methods=['POST'])
def login():
    dados = request.get_json()
    email_bruto = dados.get('email')
    senha_pin = dados.get('senha_pin') # A senha permanece intocável (Case Sensitive)

    if not email_bruto or not senha_pin:
        return jsonify({"erro": "E-mail e senha são obrigatórios!"}), 400

    # AJUSTE: Compara usando o e-mail em minúsculas
    email_formatado = email_bruto.strip().lower()

    conexao = conectar_banco()
    cursor = conexao.cursor()
    cursor.execute("SELECT id, nome FROM usuarios WHERE email = ? AND senha_pin = ?", (email_formatado, senha_pin))
    usuario = cursor.fetchone()
    conexao.close()

    if usuario:
        return jsonify({
            "mensagem": "Login aprovado", 
            "usuario_id": usuario[0], 
            "nome": usuario[1]
        }), 200
    else:
        return jsonify({"erro": "E-mail ou PIN incorretos."}), 401


# ---------------------------------------------------------
# LIGAR O SERVIDOR
# ---------------------------------------------------------
if __name__ == '__main__':
    print("🚀 API do Fluxo de Caixa ligada e aguardando pedidos...")
    app.run(host='0.0.0.0', port=5000, debug=True)