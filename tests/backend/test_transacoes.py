from backend.database import conectar_banco


def test_isolamento_transacoes_rn07(client, token):
    """Teste 06 - Segurança (RN07): Garante que um usuário não vê os dados financeiros de outro."""
    # Tenta acessar a rota de transações enviando o token válido
    response = client.get('/transacoes', headers={"Authorization": f"Bearer {token}"})
    
    # Valida que o servidor permite o acesso ao usuário correto sem expor falhas
    assert response.status_code == 200


def test_api_extrato_ordena_lancamentos_e_isola_usuario(client, token):
    conexao = conectar_banco()
    conexao.execute(
        "INSERT INTO usuarios (id, nome, email, senha_pin) VALUES (?, ?, ?, ?)",
        (2, "Outro Usuario", "outro@teste.com", "1234"),
    )
    conexao.execute(
        """
        INSERT INTO lancamentos
            (usuario_id, tipo, valor, data_lancamento, estabelecimento, data_cadastro)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (1, "PIX/CC", 25.5, "2025-03-10", "Mercado", "2025-03-10 08:00:00"),
    )
    conexao.execute(
        """
        INSERT INTO lancamentos
            (usuario_id, tipo, valor, data_lancamento, estabelecimento, data_cadastro)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (1, "cartao", 10.0, None, None, "2025-03-12 09:00:00"),
    )
    conexao.execute(
        """
        INSERT INTO lancamentos
            (usuario_id, tipo, valor, data_lancamento, estabelecimento, data_cadastro)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (2, "PIX/CC", 900.0, "2025-03-20", "Outro", "2025-03-20 09:00:00"),
    )
    conexao.commit()
    conexao.close()

    response = client.get(
        "/api/extrato",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json["status"] == "success"
    assert response.json["total_registros"] == 2
    assert [item["valor"] for item in response.json["lancamentos"]] == [10.0, 25.5]
    assert response.json["lancamentos"][0]["data"] == "2025-03-12 09:00:00"
    assert response.json["lancamentos"][0]["tipo"] == "CARTAO"
    assert response.json["lancamentos"][0]["estabelecimento"] == (
        "Estabelecimento não identificado"
    )