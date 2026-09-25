import os
import io
from unittest.mock import patch
from PIL import Image
from backend.app import app
from backend.database import inicializar_banco

@patch('backend.routes.ocr.pytesseract.image_to_string')
def test_upload_formato_valido(mock_ocr, tmp_path):
    """Garante que formatos permitidos (.png, .jpg, .pdf) são aceites"""
    mock_ocr.return_value = ""
    db_path = tmp_path / "fluxo_caixa_ocr_teste.db"
    os.environ["DB_PATH"] = str(db_path)
    os.environ["JWT_SECRET_KEY"] = "chave-falsa-apenas-para-testes-com-32-bytes"
    app.config['TESTING'] = True
    inicializar_banco()

    with app.test_client() as cliente:
        # 1. Cria utilizador e faz login para obter o token JWT
        cliente.post('/cadastro', json={"nome": "OCR User", "email": "ocr@exemplo.com", "senha_pin": "123456"})
        resp_login = cliente.post('/login', json={"email": "ocr@exemplo.com", "senha_pin": "123456"})
        token = resp_login.get_json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Simula o envio de um talão em formato PNG válido
        imagem_memoria = io.BytesIO()
        Image.new('RGB', (10, 10), color='white').save(imagem_memoria, format='PNG')
        imagem_memoria.seek(0)
        ficheiro_falso = (imagem_memoria, "talao.png")
        
        resposta = cliente.post('/ocr/upload', headers=headers, data={
            'ficheiro': ficheiro_falso
        })

        assert resposta.status_code == 200
        assert resposta.get_json()["mensagem"] == "Comprovativo processado com sucesso!"

def test_upload_formato_bloqueado(tmp_path):
    """Garante que formatos perigosos ou não suportados (.txt, .exe) são bloqueados (Segurança)"""
    db_path = tmp_path / "fluxo_caixa_ocr_teste2.db"
    os.environ["DB_PATH"] = str(db_path)
    os.environ["JWT_SECRET_KEY"] = "chave-falsa-apenas-para-testes-com-32-bytes"
    app.config['TESTING'] = True
    inicializar_banco()

    with app.test_client() as cliente:
        # 1. Faz login
        cliente.post('/cadastro', json={"nome": "OCR User 2", "email": "ocr2@exemplo.com", "senha_pin": "123456"})
        resp_login = cliente.post('/login', json={"email": "ocr2@exemplo.com", "senha_pin": "123456"})
        token = resp_login.get_json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Tenta enviar um ficheiro TXT (Proibido pelas regras de segurança)
        ficheiro_proibido = (io.BytesIO(b"texto malicioso ou invalido"), "documento.txt")
        
        resposta = cliente.post('/ocr/upload', headers=headers, data={
            'ficheiro': ficheiro_proibido
        })

        # Deve barrar com erro 400
        assert resposta.status_code == 400
        assert resposta.get_json()["erro"] == "Formato de ficheiro não suportado."

@patch('backend.routes.ocr.pytesseract.image_to_string')
def test_extracao_texto_ocr_com_sucesso(mock_ocr, tmp_path):
    """Simula a extração de texto de uma imagem sem usar o binário real no CI/CD."""
    # Configura o simulador para devolver um texto fictício
    mock_ocr.return_value = "Supermercado Assado Raiz\nTotal: R$ 150,00"

    db_path = tmp_path / "fluxo_caixa_ocr_teste3.db"
    os.environ["DB_PATH"] = str(db_path)
    os.environ["JWT_SECRET_KEY"] = "chave-teste"
    app.config['TESTING'] = True
    inicializar_banco()

    with app.test_client() as cliente:
        # Autenticação
        cliente.post('/cadastro', json={"nome": "User", "email": "ocr3@exemplo.com", "senha_pin": "123456"})
        resp_login = cliente.post('/login', json={"email": "ocr3@exemplo.com", "senha_pin": "123456"})
        token = resp_login.get_json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Cria uma imagem falsa em memória
        imagem_memoria = io.BytesIO()
        Image.new('RGB', (10, 10), color='white').save(imagem_memoria, format='PNG')
        imagem_memoria.seek(0)
        
        # Faz o upload
        resposta = cliente.post('/ocr/upload', headers=headers, data={
            'ficheiro': (imagem_memoria, "talao.png")
        })

        dados = resposta.get_json()
        assert resposta.status_code == 200
        assert dados["mensagem"] == "Comprovativo processado com sucesso!"
        assert dados["texto_bruto"] == "Supermercado Assado Raiz\nTotal: R$ 150,00"
        mock_ocr.assert_called_once()
