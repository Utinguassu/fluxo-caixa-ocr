import math
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.database import obter_conexao
from backend.services.saldo_service import SaldoService

saldo_bp = Blueprint('saldo', __name__)

@saldo_bp.route('/saldo', methods=['GET'])
@jwt_required()
def obter_saldo():
    usuario_id = get_jwt_identity()
    conn = obter_conexao()
    cursor = conn.cursor()

    # 1. Busca o saldo inicial mais recente (Regra RN05.01)
    cursor.execute('''
        SELECT valor FROM historico_saldos 
        WHERE usuario_id = ? 
        ORDER BY data_cadastro DESC LIMIT 1
    ''', (usuario_id,))
    saldo_row = cursor.fetchone()
    
    # Se o usuário ainda não cadastrou saldo inicial, assume 0.0
    saldo_inicial = saldo_row['valor'] if saldo_row else 0.0

    # 2. Busca todas as transações do usuário logado (Regra RN07)
    cursor.execute('''
        SELECT valor FROM transacoes 
        WHERE usuario_id = ?
    ''', (usuario_id,))
    transacoes_rows = cursor.fetchall()
    
    # Converte o retorno do banco para uma lista de dicionários para o Service
    transacoes = [{"valor": row['valor']} for row in transacoes_rows]

    conn.close()

    # 3. Utiliza o motor financeiro blindado para calcular o valor exato (CARD-06)
    saldo_atual = SaldoService.calcular(saldo_inicial, transacoes)

    return jsonify({"saldo_atual": saldo_atual}), 200


@saldo_bp.route('/api/saldo', methods=['GET'])
@jwt_required()
def consultar_saldo_inicial():
    """Retorna o saldo inicial mais recente do usuário autenticado, se houver."""
    usuario_id = get_jwt_identity()
    conexao = obter_conexao()
    try:
        cursor = conexao.cursor()
        cursor.execute('''
            SELECT valor FROM saldos
            WHERE usuario_id = ?
            ORDER BY data_cadastro DESC LIMIT 1
        ''', (usuario_id,))
        resultado = cursor.fetchone()

        if resultado is None:
            return jsonify({"precisa_saldo_inicial": True}), 200

        saldo_inicial = resultado['valor']
        cursor.execute('''
            SELECT COALESCE(SUM(valor), 0) AS total_gasto
            FROM lancamentos
            WHERE usuario_id = ?
        ''', (usuario_id,))
        resultado_debitos = cursor.fetchone()
        total_debitos = resultado_debitos['total_gasto']
    finally:
        conexao.close()

    return jsonify({
        "precisa_saldo_inicial": False,
        "saldo_inicial": saldo_inicial,
        "total_debitos": total_debitos,
        "saldo_atualizado": saldo_inicial - total_debitos,
    }), 200


@saldo_bp.route('/api/saldo', methods=['POST'])
@jwt_required()
def cadastrar_saldo():
    """Cadastra um novo saldo inicial sem apagar o histórico anterior."""
    dados = request.get_json(silent=True)
    if not isinstance(dados, dict) or dados.get('valor') is None:
        return jsonify({"erro": "Valor é obrigatório"}), 400

    try:
        novo_valor = float(dados['valor'])
    except (TypeError, ValueError):
        return jsonify({"erro": "Valor deve ser numérico"}), 400

    if not math.isfinite(novo_valor):
        return jsonify({"erro": "Valor deve ser numérico"}), 400

    usuario_id = get_jwt_identity()
    conexao = obter_conexao()
    try:
        conexao.execute(
            "INSERT INTO saldos (usuario_id, valor) VALUES (?, ?)",
            (usuario_id, novo_valor),
        )
        conexao.commit()
    finally:
        conexao.close()

    return jsonify({"mensagem": "Saldo cadastrado com sucesso!"}), 201