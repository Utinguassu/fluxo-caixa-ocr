import os
from flask import Flask
from flask_cors import CORS
from flasgger import Swagger
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

from backend.database import inicializar_banco
from backend.routes.auth import auth_bp
from backend.routes.transacoes import transacoes_bp
from backend.routes.ocr import ocr_bp

load_dotenv()

app = Flask(__name__)
CORS(app)
Swagger(app)

app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
if not app.config["JWT_SECRET_KEY"]:
    raise ValueError("FALHA CRÍTICA: A variável JWT_SECRET_KEY não está configurada!")

jwt = JWTManager(app)

# Inicializa banco de dados
inicializar_banco()

# Regista os módulos (Blueprints)
app.register_blueprint(auth_bp)
app.register_blueprint(transacoes_bp)
app.register_blueprint(ocr_bp)

if __name__ == '__main__':
    print("🚀 Motor iniciado. API limpa e modular rodando em http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)