from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.database import conectar_banco

transacoes_bp = Blueprint('transacoes', __name__)

@transacoes_bp.route('/transacoes', methods=['POST'])
@jwt_required() # <--- A Mágica de Segurança (Exige o Token)
def criar_transacao():
    usuario_id = get_jwt_identity() # Pega o ID de quem está logado pelo Token
    dados = request.get_json() or {}
    
    tipo = dados.get('tipo')
    valor = dados.get('valor')
    descricao = dados.get('descricao')

    if not tipo or not valor or not descricao:
        return jsonify({"erro": "Tipo, valor e descrição são obrigatórios."}), 400

    conexao = conectar_banco()
    cursor = conexao.cursor()
    cursor.execute(
        "INSERT INTO transacoes (usuario_id, tipo, valor, descricao) VALUES (?, ?, ?, ?)",
        (usuario_id, tipo, float(valor), descricao)
    )
    conexao.commit()
    conexao.close()
    
    return jsonify({"mensagem": "Transação registrada com sucesso!"}), 201

@transacoes_bp.route('/transacoes', methods=['GET'])
@jwt_required()
def listar_transacoes():
    usuario_id = get_jwt_identity() # Garante Isolamento RN07
    
    conexao = conectar_banco()
    cursor = conexao.cursor()
    # Busca APENAS as transações do dono do token
    cursor.execute("SELECT id, tipo, valor, descricao, data FROM transacoes WHERE usuario_id = ?", (usuario_id,))
    linhas = cursor.fetchall()
    conexao.close()

    transacoes = [{"id": l[0], "tipo": l[1], "valor": l[2], "descricao": l[3], "data": l[4]} for l in linhas]
    return jsonify(transacoes), 200