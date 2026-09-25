import os
import io
from backend.app import app
from backend.database import inicializar_banco

def test_upload_formato_valido(tmp_path):
    """Garante que formatos permitidos (.png, .jpg, .pdf) são aceites"""
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
        ficheiro_falso = (io.BytesIO(b"conteudo binario de imagem simulada"), "talao.png")
        
        resposta = cliente.post('/ocr/upload', headers=headers, data={
            'ficheiro': ficheiro_falso
        })

        assert resposta.status_code == 200
        assert resposta.get_json()["mensagem"] == "Ficheiro recebido e validado com sucesso!"

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
