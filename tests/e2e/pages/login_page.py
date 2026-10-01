class LoginPage:
    def __init__(self, page):
        self.page = page
        self.url = "http://localhost:5000/"

        # Mapeamento dos elementos (Locators)
        self.titulo = page.locator("h2")
        self.input_email = page.locator("#email")
        self.input_senha = page.locator("#senha")
        self.botao_acessar = page.locator('button[type="submit"]')

    def acessar_pagina(self):
        """Abre o navegador na URL do sistema."""
        self.page.goto(self.url)

    def preencher_login(self, email, senha):
        """Preenche os dados do formulário."""
        self.input_email.fill(email)
        self.input_senha.fill(senha)

    def submeter_formulario(self):
        """Clica no botão de acesso."""
        self.botao_acessar.click()
