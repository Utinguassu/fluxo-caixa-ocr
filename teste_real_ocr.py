import os
from backend.app import app
from backend.database import inicializar_banco

# 1. Configura um ambiente rápido para o teste
os.environ["DB_PATH"] = "banco_teste_real.db"
os.environ["JWT_SECRET_KEY"] = "chave-secreta-teste-real"
inicializar_banco()

print("🤖 A iniciar teste REAL do Motor OCR...")

with app.test_client() as cliente:
    # 2. Fazer Cadastro e Login para obter a "chave" da porta (JWT)
    cliente.post('/cadastro', json={"nome": "Teste Real", "email": "real@teste.com", "senha_pin": "123456"})
    login = cliente.post('/login', json={"email": "real@teste.com", "senha_pin": "123456"})
    token = login.get_json().get("token")
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Pegar na fotografia física (Ajustado para o nome exato da sua imagem!)
    caminho_imagem = "talao_real.PNG.png" 
    
    try:
        with open(caminho_imagem, "rb") as imagem_fisica:
            print(f"📸 A enviar a imagem '{caminho_imagem}' para a API...")
            
            # 4. Fazer o Upload!
            resposta = cliente.post(
                '/ocr/upload', 
                headers=headers,
                data={"ficheiro": (imagem_fisica, caminho_imagem)}
            )
            
            # 5. Imprimir a resposta COMPLETA para vermos o erro
            dados = resposta.get_json()
            print("\n" + "="*50)
            print("🔍 RESPOSTA BRUTA DA API:")
            print(dados) # Isto vai mostrar o erro escondido!
            print("="*50 + "\n")
            
    except FileNotFoundError:
        print(f"❌ ERRO: Não encontrei a foto '{caminho_imagem}' na raiz do projeto. Verifique o nome!")
