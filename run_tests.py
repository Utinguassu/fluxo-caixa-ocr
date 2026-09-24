import os
import datetime
import subprocess

def executar_testes():
    # 1. Garante que a pasta de relatórios existe (organização limpa)
    pasta_relatorios = "relatorios"
    os.makedirs(pasta_relatorios, exist_ok=True)

    # 2. Gera um carimbo de data e hora atual (ex: 20260924_203015)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_relatorio = os.path.join(pasta_relatorios, f"relatorio_testes_{timestamp}.html")

    print("🚀 A iniciar a suíte de testes automatizados...")

    # 3. Executa o pytest direcionando a saída para o relatório HTML na pasta
    comando = [
        "pytest", 
        f"--html={caminho_relatorio}", 
        "--self-contained-html", 
        "-v"
    ]
    
    resultado = subprocess.run(comando)

    # 4. Feedback visual no terminal
    if resultado.returncode == 0:
        print(f"\n✨ SUCESSO! Todos os testes passaram.")
        print(f"📂 Relatório visual guardado em: {caminho_relatorio}\n")
    else:
        print(f"\n⚠️ ALERTA: Alguns testes falharam.")
        print(f"📂 Verifique os detalhes no relatório: {caminho_relatorio}\n")

if __name__ == "__main__":
    executar_testes()
