from flask import Blueprint, request, jsonify
from backend.database import obter_conexao
from flask_jwt_extended import jwt_required, get_jwt_identity
import math
from datetime import datetime
from collections import defaultdict

saldo_bp = Blueprint('saldo', __name__)

@saldo_bp.route('/api/resumo', methods=['GET'])
@jwt_required()
def obter_resumo():
    """
    Retorna o resumo financeiro atualizado, com saldo atual e categorização.
    """
    usuario_id = get_jwt_identity()
    conexao = obter_conexao()
    cursor = conexao.cursor()

    try:
        # Busca o último saldo inicial configurado pelo usuário na tabela `saldo`
        cursor.execute('''
            SELECT valor FROM saldo 
            WHERE usuario_id = ? 
            ORDER BY data_cadastro DESC LIMIT 1
        ''', (usuario_id,))
        saldo_inicial_row = cursor.fetchone()
        
        saldo_inicial = saldo_inicial_row['valor'] if saldo_inicial_row else 0.0

        # Busca as receitas, despesas e suas categorias usando a nova tabela de `lancamentos`
        cursor.execute('''
            SELECT tipo, valor, categoria 
            FROM lancamentos 
            WHERE usuario_id = ?
        ''', (usuario_id,))
        transacoes = cursor.fetchall()
        
        total_despesas = 0.0
        total_receitas = 0.0
        despesas_por_categoria = defaultdict(float)

        for t in transacoes:
            valor = float(t['valor'])
            tipo = t['tipo'].strip().lower()
            categoria = t['categoria'].strip() if t['categoria'] else "Outros"

            if tipo == "despesa":
                total_despesas += valor
                despesas_por_categoria[categoria] += valor
            elif tipo == "receita":
                total_receitas += valor

        saldo_atual = (saldo_inicial + total_receitas) - total_despesas

        return jsonify({
            "saldo_inicial_configurado": saldo_inicial,
            "saldo_atual": saldo_atual,
            "total_despesas": total_despesas,
            "total_receitas": total_receitas,
            "despesas_por_categoria": dict(despesas_por_categoria)
        }), 200

    except Exception as e:
        print(f"Erro ao obter resumo financeiro: {e}")
        return jsonify({"erro": "Erro interno ao processar o resumo financeiro"}), 500
    finally:
        conexao.close()


@saldo_bp.route('/api/saldo', methods=['POST'])
@jwt_required()
def cadastrar_saldo():
    """
    Cadastra um novo saldo inicial sem apagar os registros anteriores.
    """
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
        # Trocado de 'saldos' para 'saldo' na query de Inserção
        conexao.execute(
            "INSERT INTO saldo (usuario_id, valor) VALUES (?, ?)",
            (usuario_id, novo_valor),
        )
        conexao.commit()
    except Exception as e:
        print(f"Erro ao cadastrar saldo: {e}")
        return jsonify({"erro": "Erro interno no banco de dados"}), 500
    finally:
        conexao.close()

    return jsonify({"mensagem": "Saldo inicial definido com sucesso!"}), 201