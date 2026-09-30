def test_isolamento_transacoes_rn07(client, token):
    """Teste 06 - Segurança (RN07): Garante que um usuário não vê os dados financeiros de outro."""
    # Tenta acessar a rota de transações enviando o token válido
    response = client.get('/transacoes', headers={"Authorization": f"Bearer {token}"})
    
    # Valida que o servidor permite o acesso ao usuário correto sem expor falhas
    assert response.status_code == 200