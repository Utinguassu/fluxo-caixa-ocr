import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.services.ocr_service import processar_imagem_ocr
from backend.database import obter_conexao

ocr_bp = Blueprint('ocr_bp', __name__)

# Extensões permitidas para upload
EXTENSOES_PERMITIDAS = {'png', 'jpg', 'jpeg', 'pdf'}

def arquivo_permitido(nome_arquivo):
    return '.' in nome_arquivo and nome_arquivo.rsplit('.', 1)[1].lower() in EXTENSOES_PERMITIDAS

@ocr_bp.route('/ocr/upload', methods=['POST'])
@jwt_required()
def upload_ocr():
    usuario_id = get_jwt_identity()

    if 'file' not in request.files:
        return jsonify({"erro": "Nenhum arquivo enviado."}), 400

    arquivo = request.files['file']

    if arquivo.filename == '':
        return jsonify({"erro": "Nenhum arquivo selecionado."}), 400

    if not arquivo_permitido(arquivo.filename):
        return jsonify({"erro": "Formato de arquivo não suportado. Use PNG, JPG, JPEG ou PDF."}), 400

    try:
        # Processa a imagem utilizando o serviço de OCR isolado
        resultado_ocr = processar_imagem_ocr(arquivo)
        
        dados = resultado_ocr.get("dados_extraidos", {})
        valor = dados.get("valor", 0.0)
        data = dados.get("data", "")
        descricao = dados.get("descricao", "Despesa OCR")
        tipo = dados.get("tipo", "despesa")

        # Persiste a transação na base de dados ativa
        conn = obter_conexao()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO transacoes (usuario_id, valor, data, descricao, tipo)
            VALUES (?, ?, ?, ?, ?)
            """,
            (usuario_id, valor, data, descricao, tipo)
        )
        conn.commit()
        transacao_id = cursor.lastrowid
        conn.close()

        return jsonify({
            "mensagem": "Comprovativo processado e transação guardada com sucesso!",
            "transacao_id": transacao_id,
            "dados_extraidos": dados,
            "texto_bruto": resultado_ocr.get("texto_bruto", "")
        }), 200

    except Exception as e:
        return jsonify({"erro": f"Erro ao processar o arquivo: {str(e)}"}), 500