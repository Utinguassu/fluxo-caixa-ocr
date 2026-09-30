from flask import Blueprint, jsonify
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