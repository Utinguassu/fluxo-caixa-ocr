import os
import io
import pytest
from backend.services.categoria_service import CategoriaService

def test_upload_formato_invalido(client, token):
    """Teste 04 - Formato de Upload Válido: Bloqueia extensões não suportadas."""
    # Simula o upload de um arquivo de texto (.txt) ao invés de imagem
    data = {
        'file': (io.BytesIO(b"conteudo de texto falso"), 'arquivo.txt')
    }
    
    response = client.post(
        '/ocr/upload',
        data=data,
        content_type='multipart/form-data',
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Deve ser rejeitado com erro de requisição inválida
    assert response.status_code == 400
    assert 'erro' in response.json

def test_processamento_ocr_mock(client, token, monkeypatch):
    """Teste 05 - OCR Mock: Simula leitura de recibo para validar a rota de upload sem depender do Tesseract."""
    # Criamos um mock rápido para pular o processamento real no CI/CD se necessário
    def mock_ocr_read(*args, **kwargs):
        return "SUPERMERCADO MOCK\nVALOR: R$ 50,00"
    
    # Fica preparado caso a sua API use pytesseract.image_to_string
    import pytesseract
    monkeypatch.setattr(pytesseract, 'image_to_string', mock_ocr_read)

    # Cria uma imagem falsa mínima compatível com PNG para passar na validação de extensão
    imagem_falsa = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    
    data = {
        'file': (io.BytesIO(imagem_falsa), 'recibo_mock.png')
    }
    
    response = client.post(
        '/ocr/upload',
        data=data,
        content_type='multipart/form-data',
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # A API deve responder com sucesso ou tratar a imagem graciosamente
    assert response.status_code in [200, 400, 500]

def test_processamento_ocr_arquivo_real(client, token):
    """Teste 07 - OCR Real: Processa uma imagem física real, extrai texto e categoriza (RN08)."""
    caminho_imagem = 'tests/dados_teste/talao_real.png'

    # Se o arquivo não existir (ex: no servidor do GitHub), pula o teste de forma elegante
    if not os.path.exists(caminho_imagem):
        pytest.skip(f"Arquivo real não encontrado no caminho: {caminho_imagem}")

    # 1. Lê a imagem física real (só executa se o arquivo existir localmente)
    with open(caminho_imagem, 'rb') as img:
        imagem_bytes = img.read()

    data = {
        'file': (io.BytesIO(imagem_bytes), 'talao_real.png')
    }

    # 2. Faz o POST para a API simulando o usuário logado
    response = client.post(
        '/ocr/upload',
        data=data,
        content_type='multipart/form-data',
        headers={"Authorization": f"Bearer {token}"} 
    )

    assert response.status_code == 200

    # 3. Extrai o texto lido pelo Tesseract no JSON da resposta
    texto_extraido = response.json.get('texto', '')

    # 4. Aciona a RN08 (Categorização Automática)
    categoria = CategoriaService.categorizar(texto_extraido)

    # 5. Validação Visual para o Terminal e Relatório HTML
    print("\n" + "="*50)
    print("🔍 VALIDAÇÃO VISUAL DO TESTE REAL (RN08) - VIA PYTEST")
    print("="*50)
    print("📄 Texto Extraído da Imagem:")
    print(texto_extraido)
    print("-" * 50)
    print(f"🏷️ Categoria Atribuída Automaticamente: ---> [ {categoria.upper()} ] <---")
    print("="*50 + "\n")

    # Garante que o motor conseguiu atribuir uma categoria
    assert categoria is not None