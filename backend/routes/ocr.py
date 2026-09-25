import os
import platform
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from PIL import Image
import pytesseract

# Híbrido: Configuração inteligente para Windows (Local) vs Linux (Nuvem)
if platform.system() == "Windows":
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

ocr_bp = Blueprint('ocr', __name__)

EXTENSOES_PERMITIDAS = {'png', 'jpg', 'jpeg', 'pdf'}

def ficheiro_permitido(nome_ficheiro):
    return '.' in nome_ficheiro and nome_ficheiro.rsplit('.', 1)[1].lower() in EXTENSOES_PERMITIDAS

@ocr_bp.route('/ocr/upload', methods=['POST'])
@jwt_required()
def processar_comprovativo():
    if 'ficheiro' not in request.files:
        return jsonify({"erro": "Nenhum ficheiro foi enviado."}), 400

    ficheiro = request.files['ficheiro']

    if ficheiro.filename == '':
        return jsonify({"erro": "O ficheiro selecionado não tem nome."}), 400

    if not ficheiro_permitido(ficheiro.filename):
        return jsonify({"erro": "Formato de ficheiro não suportado."}), 400

    try:
        # Carrega a imagem na memória e executa o motor OCR (idioma: português)
        imagem = Image.open(ficheiro.stream)
        texto_extraido = pytesseract.image_to_string(imagem, lang='por')
        
        return jsonify({
            "mensagem": "Comprovativo processado com sucesso!",
            "ficheiro": ficheiro.filename,
            "texto_bruto": texto_extraido.strip()
        }), 200
        
    except Exception as e:
        return jsonify({"erro": f"Falha no processamento OCR: {str(e)}"}), 500