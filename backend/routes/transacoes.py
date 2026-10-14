import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.database import conectar_banco

transacoes_bp = Blueprint('transacoes_bp', __name__)

@transacoes_bp.route('/transacoes', methods=['POST'])
@jwt_required()
def criar_transacao():
    """
    Registra um novo lançamento/débito no sistema.
    ---
    tags:
      - Transações e Linha do Tempo
    security:
      - BearerAuth: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            tipo:
              type: string
            valor:
              type: number
            estabelecimento:
              type: string
            data_lancamento:
              type: string
    responses:
      201:
        description: Lançamento criado com sucesso.
      400:
        description: Dados inválidos.
      500:
        description: Erro interno.
    """
    usuario_id = get_jwt_identity()
    dados = request.get_json() or {}
    
    tipo = dados.get('tipo', 'OUTROS')
    valor = dados.get('valor')
    estabelecimento = dados.get('estabelecimento', '')
    data_lancamento = dados.get('data_lancamento')
    
    if valor is None:
        return jsonify({"erro": "O campo valor é obrigatório!"}), 400
        
    try:
        conexao = conectar_banco()
        cursor = conexao.cursor()
        
        cursor.execute("""
          INSERT INTO lancamentos (usuario_id, tipo, valor, estabelecimento, data_lancamento)
          VALUES (?, ?, ?, ?, ?)
        """, (usuario_id, tipo, valor, estabelecimento, data_lancamento))
        
        conexao.commit()
        conexao.close()
        
        return jsonify({"mensagem": "Lançamento registrado com sucesso!"}), 201
    except Exception as e:
        logging.error(f"Erro ao criar lançamento: {str(e)}")
        return jsonify({"erro": "Erro interno ao registrar lançamento."}), 500


@transacoes_bp.route('/api/extrato', methods=['GET'])
@jwt_required()
def obter_extrato():
    """
    Retorna a linha do tempo de lançamentos (Extrato).
    ---
    tags:
      - Transações e Linha do Tempo
    security:
      - BearerAuth: []
    responses:
      200:
        description: Extrato ordenado do mais recente para o mais antigo.
    """
    usuario_id = get_jwt_identity()
    try:
        conexao = conectar_banco()
        cursor = conexao.cursor()
        
        cursor.execute("""
            SELECT id, tipo, valor, data_lancamento, estabelecimento, data_cadastro 
            FROM lancamentos 
            WHERE usuario_id = ? 
            ORDER BY COALESCE(data_lancamento, data_cadastro) DESC, id DESC
        """, (usuario_id,))
        
        linhas = cursor.fetchall()
        conexao.close()
        
        extrato = []
        for linha in linhas:
            data_final = linha['data_lancamento'] if linha['data_lancamento'] else linha['data_cadastro']
            extrato.append({
                "id": linha['id'],
                "tipo": linha['tipo'].upper() if linha['tipo'] else "OUTROS",
                "valor": float(linha['valor']),
                "data": data_final,
                "estabelecimento": linha['estabelecimento'] or "Estabelecimento não identificado"
            })
            
        return jsonify({
            "status": "success",
            "total_registros": len(extrato),
            "lancamentos": extrato
        }), 200
    except Exception as e:
        logging.error(f"Erro ao buscar extrato: {str(e)}")
        return jsonify({"status": "error", "mensagem": "Erro interno ao processar extrato."}), 500