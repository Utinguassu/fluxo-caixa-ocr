import re

class CategoriaService:
    # Este é o nosso dicionário de palavras-chave. O detetive vai procurar por elas.
    categorizacao_regras = {
        "Alimentação": ["supermercado", "mercado", "restaurante", "lanche", "pizzaria", "padaria", "food", "café"],
        "Transporte": ["posto", "combustivel", "gasolina", "uber", "99", "estacionamento", "pedágio"],
        "Lazer": ["cinema", "teatro", "ingresso", "show", "viagem", "hotel"],
        "Serviços": ["farmacia", "drogaria", "agua", "luz", "internet", "telefone"]
    }

    @classmethod
    def categorizar(cls, texto_ocr: str) -> str:
        """
        Analisa o texto extraído pelo OCR e retorna a categoria correspondente.
        Se não encontrar nenhuma palavra conhecida, coloca na gaveta 'Outros'.
        """
        if not texto_ocr:
            return "Outros"
        
        texto_minusculo = texto_ocr.lower()

        # O detetive olha para cada gaveta (categoria) e suas palavras-chave
        for categoria, palavras_chave in cls.categorizacao_regras.items():
            for palavra in palavras_chave:
                # Procura a palavra exata no texto
                if re.search(r'\b' + re.escape(palavra) + r'\b', texto_minusculo):
                    return categoria
                    
        # Se não achou nada, devolve "Outros"
        return "Outros"
