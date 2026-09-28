from backend.services.categoria_service import CategoriaService

def test_categorizacao_alimentacao():
    """Teste 08 - Categorização: Verifica se palavras de comida vão para Alimentação."""
    texto_recibo = "COMPROVANTE DE PAGAMENTO\nSUPERMERCADO ZAFFARI\nVALOR: R$ 150,00"
    resultado = CategoriaService.categorizar(texto_recibo)
    assert resultado == "Alimentação"

def test_categorizacao_transporte():
    """Teste 09 - Categorização: Verifica se apps de corrida vão para Transporte."""
    texto_recibo = "Recibo de Viagem Uber Technologies\nTotal: 25.50"
    resultado = CategoriaService.categorizar(texto_recibo)
    assert resultado == "Transporte"

def test_categorizacao_lazer_case_insensitive():
    """Teste 10 - Categorização: Verifica se o detetive ignora letras maiúsculas/minúsculas."""
    texto_recibo = "CINEMA GNC - Ingresso VIP"
    resultado = CategoriaService.categorizar(texto_recibo)
    assert resultado == "Lazer"

def test_categorizacao_desconhecida():
    """Teste 11 - Categorização: Verifica se texto sem palavras-chave vai para Outros."""
    texto_recibo = "LOJA DE PARAFUSOS IRMAOS SILVA\nR$ 10,00"
    resultado = CategoriaService.categorizar(texto_recibo)
    assert resultado == "Outros"
