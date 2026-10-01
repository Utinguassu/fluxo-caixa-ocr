from tests.e2e.pages.login_page import LoginPage


def test_login_interface_e_falha(page):
    """
    Cenário (BDD): Usuário tenta fazer login com dados incorretos e vê o alerta.

    Dado (Given) que o usuário acessa a tela de Login
    E (And) visualiza a mensagem de "Bem-vindo ao projeto"
    Quando (When) ele preencher um e-mail e senha inválidos
    E (And) clicar em 'Acessar Sistema'
    Então (Then) o navegador deve exibir um alerta de acesso negado
    """
    login_page = LoginPage(page)

    # 1. Dado (Acessa a página)
    login_page.acessar_pagina()

    # 2. E (Valida se o texto correto da Opção 3 está na tela)
    assert "Bem-vindo ao projeto de" in login_page.titulo.inner_text()

    # Prepara o Playwright para interceptar a caixa de alerta nativa do navegador (window.alert)
    mensagens_alerta = []
    page.on("dialog", lambda dialog: (mensagens_alerta.append(dialog.message), dialog.accept()))

    # 3. Quando (Preenche os dados falsos)
    login_page.preencher_login("usuario_falso@teste.com", "000000")

    # 4. E (Clica no botão)
    login_page.submeter_formulario()

    # Aguarda um pequeno instante para a API responder e o alerta ser disparado
    page.wait_for_timeout(1000)

    # 5. Então (Valida se o alerta de erro apareceu)
    assert len(mensagens_alerta) > 0
    assert "Acesso negado" in mensagens_alerta[0]