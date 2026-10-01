import os
import pytest
from datetime import datetime

# 1. Gera o nome da pasta incremental com data e hora exatas
agora = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
PASTA_EVIDENCIAS = os.path.join("relatorios", "evidencias_e2e", f"{agora}_teste_end_to_end_Playwright")

# 2. Configura o Playwright para usar o Chrome da máquina e gravar VÍDEOS automaticamente
@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "record_video_dir": PASTA_EVIDENCIAS
    }

# Força o navegador a utilizar o canal 'chrome' do seu Windows por padrão
@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    return {
        **browser_type_launch_args,
        "channel": "chrome"
    }

# 3. Tira um PRINT de tela automaticamente ao final de cada teste
@pytest.fixture(autouse=True)
def capturar_evidencia(page, request):
    yield  # Executa o teste
    
    os.makedirs(PASTA_EVIDENCIAS, exist_ok=True)
    nome_teste = request.node.name
    caminho_print = os.path.join(PASTA_EVIDENCIAS, f"{nome_teste}.png")
    
    page.screenshot(path=caminho_print, full_page=True)

