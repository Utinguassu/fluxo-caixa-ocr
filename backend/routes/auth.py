import sqlite3
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from backend.database import conectar_banco

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/cadastro', methods=['POST'])
def cadastrar_usuario():
    """
    Cadastra um novo utilizador no sistema.
        ---
        tags:
            - Autenticação
        parameters: [{in: body, name: body, required: true, schema: {type: object, required: [nome, email, senha_pin], properties: {nome: {type: string}, email: {type: string, format: email}, senha_pin: {type: string}, telefone: {type: string}}}}]
        responses:
            201:
                description: Utilizador criado com sucesso.
            400:
                description: Erro de validação ou e-mail duplicado.
    """
    dados = request.get_json() or {}
    nome = dados.get('nome')
    email_bruto = dados.get('email')
    senha_pin = dados.get('senha_pin')
    telefone = dados.get('telefone')

    if not nome or not email_bruto or not senha_pin:
        return jsonify({"erro": "Todos os campos são obrigatórios!"}), 400

    email_formatado = email_bruto.strip().lower()

    try:
        conexao = conectar_banco()
        cursor = conexao.cursor()
        cursor.execute(
            "INSERT INTO usuarios (nome, email, senha_pin, telefone) VALUES (?, ?, ?, ?)",
            (nome, email_formatado, senha_pin, telefone)
        )
        conexao.commit()
        conexao.close()
        return jsonify({"mensagem": "Usuário cadastrado com sucesso!"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"erro": "Este e-mail já está cadastrado."}), 400


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Autentica um utilizador e devolve o token JWT.
        ---
        tags:
            - Autenticação
        parameters: [{in: body, name: body, required: true, schema: {type: object, required: [email, senha_pin], properties: {email: {type: string, format: email}, senha_pin: {type: string}}}}]
        responses:
            200:
                description: Login efetuado com sucesso; retorna o token JWT.
            400:
                description: E-mail ou senha ausente.
            401:
                description: Credenciais inválidas.
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
        token_acesso = create_access_token(identity=str(usuario[0]))
        return jsonify({"mensagem": "Login aprovado", "access_token": token_acesso, "nome": usuario[1]}), 200
    else:
        return jsonify({"erro": "E-mail ou PIN incorretos."}), 401