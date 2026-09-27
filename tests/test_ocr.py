import io
import os
import pytest
from unittest.mock import patch

def test_upload_formato_nao_suportado(client, token):
    """Teste 04 - Validação de Arquivo: Bloqueia upload de formatos não suportados (ex: .txt)."""
    data = {
        'file': (io.BytesIO(b"conteudo invalido"), 'teste.txt')
    }
    
    response = client.post(
        '/ocr/upload', 
        data=data, 
        content_type='multipart/form-data',
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 400
    assert "Formato de arquivo não suportado" in response.get_json()["erro"]

@patch('backend.services.ocr_service.pytesseract.image_to_string')
def test_processamento_ocr_sucesso(mock_tesseract, client, token):
    """Teste 05 - Fluxo de OCR (Mock): Valida a extração simulada de texto de uma imagem."""
    mock_tesseract.return_value = "Pagueveloz\nR$ 150,50\n24/09/2026"
    imagem_png_valida = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'

    data = {
        'file': (io.BytesIO(imagem_png_valida), 'talao.png')
    }

    response = client.post(
        '/ocr/upload', 
        data=data, 
        content_type='multipart/form-data',
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200

def test_processamento_ocr_arquivo_real(client, token):
    """Teste 07 - OCR Real: Processa uma imagem física real e salva os dados no banco de testes."""
    caminho_imagem = 'tests/dados_teste/talao_real.png'
    
    # Se o arquivo não existir na pasta, o Pytest pula o teste de forma elegante
    if not os.path.exists(caminho_imagem):
        pytest.skip(f"Arquivo real não encontrado no caminho: {caminho_imagem}")

    # Abre o arquivo de imagem real em modo leitura de bytes ('rb')
    with open(caminho_imagem, 'rb') as imagem_real:
        data = {
            'file': (imagem_real, 'talao_real.png')
        }

        # Envia para a API real, acionando o Tesseract verdadeiro no seu computador
        response = client.post(
            '/ocr/upload', 
            data=data, 
            content_type='multipart/form-data',
            headers={"Authorization": f"Bearer {token}"}
        )

    # Verifica se a API processou e gravou no banco de teste com sucesso
    assert response.status_code == 200