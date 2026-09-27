import os
import re
import platform
import pytesseract
from PIL import Image
from datetime import datetime

# Configuração do Tesseract (Plataforma-awarness)
if platform.system() == "Windows":
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extrair_dados_transacao(texto_bruto):
    """
    Aplica expressões regulares (Regex) para extrair valor, data e estabelecimento.
    """
    dados = {
        "valor": 0.0,
        "descricao": "Despesa via OCR",
        "data": datetime.now().strftime("%Y-%m-%d"),
        "tipo": "despesa"
    }
    
    if not texto_bruto:
        return dados

    # 1. Extração do Valor (Ex: R$ 178,33)
    match_valor = re.search(r"R\$\s*([\d\.,]+)", texto_bruto)
    if match_valor:
        valor_str = match_valor.group(1)
        valor_str = valor_str.replace(".", "").replace(",", ".")
        try:
            dados["valor"] = float(valor_str)
        except ValueError:
            pass

    # 2. Extração da Data (Ex: 24 de setembro de 2026)
    meses = {
        "janeiro": "01", "fevereiro": "02", "março": "03", "abril": "04",
        "maio": "05", "junho": "06", "julho": "07", "agosto": "08",
        "setembro": "09", "outubro": "10", "novembro": "11", "dezembro": "12"
    }
    
    match_data = re.search(r"(\d{1,2})\s+de\s+([a-zçãéíóú]+)\s+de\s+(\d{4})", texto_bruto.lower())
    if match_data:
        dia, mes_nome, ano = match_data.groups()
        if mes_nome in meses:
            dados["data"] = f"{ano}-{meses[mes_nome]}-{int(dia):02d}"

    # 3. Extração do Estabelecimento / Descrição
    linhas = [l.strip() for l in texto_bruto.split("\n") if l.strip()]
    for linha in linhas:
        if "R$" not in linha and "quinta" not in linha.lower() and "transação" not in linha.lower() and len(linha) > 2:
            dados["descricao"] = linha
            break

    return dados

def processar_imagem_ocr(ficheiro_imagem):
    """
    Executa a leitura da imagem pelo Tesseract e o parsing inteligente.
    """
    imagem = Image.open(ficheiro_imagem)
    texto_bruto = pytesseract.image_to_string(imagem, lang='por')
    dados_extraidos = extrair_dados_transacao(texto_bruto)
    
    return {
        "texto_bruto": texto_bruto,
        "dados_extraidos": dados_extraidos
    }