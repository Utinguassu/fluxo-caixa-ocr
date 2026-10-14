import math

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from backend.database import conectar_banco

saldo_bp = Blueprint('saldo', __name__)


@saldo_bp.route('/api/resumo', methods=['GET'])
@saldo_bp.route('/api/saldo', methods=['GET'])
@jwt_required()
def obter_saldo():
    usuario_id = get_jwt_identity()
    conexao = conectar_banco()

    try:
        saldo_inicial = conexao.execute(
            """
            SELECT valor FROM lancamentos
            WHERE usuario_id = ? AND tipo = 'SALDO_INICIAL'
            ORDER BY data_lancamento DESC LIMIT 1
            """,
            (usuario_id,),
        ).fetchone()

        if not saldo_inicial:
            return jsonify({"precisa_saldo_inicial": True}), 200

        valor_inicial = saldo_inicial["valor"]
        total_despesas = conexao.execute(
            """
            SELECT SUM(valor) FROM lancamentos
            WHERE usuario_id = ? AND tipo != 'SALDO_INICIAL'
            """,
            (usuario_id,),
        ).fetchone()[0] or 0.0

        saldo_atualizado = valor_inicial - total_despesas

        return jsonify({
            "precisa_saldo_inicial": False,
            "saldo_inicial": float(valor_inicial),
            "total_debitos": float(total_despesas),
            "saldo_atualizado": float(saldo_atualizado),
            "saldo_atual": float(saldo_atualizado),
        }), 200
    finally:
        conexao.close()


@saldo_bp.route('/api/saldo', methods=['POST'])
@jwt_required()
def cadastrar_saldo_inicial():
    dados = request.get_json(silent=True)
    if not isinstance(dados, dict) or dados.get("valor") is None:
        return jsonify({"erro": "Valor é obrigatório"}), 400

    try:
        valor = float(dados["valor"])
    except (TypeError, ValueError):
        return jsonify({"erro": "Valor deve ser numérico"}), 400

    if not math.isfinite(valor):
        return jsonify({"erro": "Valor deve ser numérico"}), 400

    usuario_id = get_jwt_identity()
    conexao = conectar_banco()

    try:
        conexao.execute(
            """
            INSERT INTO lancamentos (usuario_id, tipo, valor, estabelecimento, data_lancamento)
            VALUES (?, 'SALDO_INICIAL', ?, 'Aporte Inicial', date('now'))
            """,
            (usuario_id, valor),
        )
        conexao.commit()
        return jsonify({"mensagem": "Saldo cadastrado com sucesso!"}), 201
    finally:
        conexao.close()