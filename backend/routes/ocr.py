import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

ocr_bp = Blueprint('ocr', __name__)

# Definimos estritamente as extensões permitidas por razões de segurança
EXTENSOES_PERMITIDAS = {'png', 'jpg', 'jpeg', 'pdf'}

def ficheiro_permitido(nome_ficheiro):
    """Verifica se o ficheiro possui uma extensão válida permitida."""
    return '.' in nome_ficheiro and \
           nome_ficheiro.rsplit('.', 1)[1].lower() in EXTENSOES_PERMITIDAS

@ocr_bp.route('/ocr/upload', methods=['POST'])
@jwt_required() # Segurança: Só utilizadores autenticados podem enviar comprovativos
def processar_comprovativo():
    """
    Endpoint para upload e processamento OCR de talões e recibos
    ---
    tags:
      - OCR
    """
    # 1. Verifica se o ficheiro foi enviado na requisição
    if 'ficheiro' not in request.files:
        return jsonify({"erro": "Nenhum ficheiro foi enviado na requisição."}), 400

    ficheiro = request.files['ficheiro']

    # 2. Verifica se o utilizador selecionou um ficheiro vazio
    if ficheiro.filename == '':
        return jsonify({"erro": "O ficheiro selecionado não tem nome."}), 400

    # 3. VALIDAÇÃO RIGOROSA DE FORMATO (Bloqueia extensões não autorizadas)
    if not ficheiro_permitido(ficheiro.filename):
        return jsonify({
            "erro": "Formato de ficheiro não suportado.",
            "formatos_permitidos": list(EXTENSOES_PERMITIDAS)
        }), 400

    # 4. Se passou na validação, o ficheiro é seguro para processamento
    nome_seguro = ficheiro.filename
    
    # (Futuramente aqui entra o motor de OCR para ler o texto do talão)
    
    return jsonify({
        "mensagem": "Ficheiro recebido e validado com sucesso!",
        "ficheiro": nome_seguro,
        "status": "Aguardando extração de dados..."
    }), 200
