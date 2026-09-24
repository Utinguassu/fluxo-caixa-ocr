import sqlite3
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from backend.database import conectar_banco

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/cadastro', methods=['POST'])
def cadastrar_usuario():
    """Registo de novo utilizador no sistema (ver doc Swagger)"""
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


@auth_bp.route('/login', methods=['POST'])
def login():
    """Autenticação de utilizador (Login)"""
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
        token_acesso = create_access_token(identity=str(usuario[0]))
        return jsonify({"mensagem": "Login aprovado", "token": token_acesso, "nome": usuario[1]}), 200
    else:
        return jsonify({"erro": "E-mail ou PIN incorretos."}), 401