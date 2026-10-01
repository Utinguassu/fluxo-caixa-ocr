class DashboardPage:
    def __init__(self, page):
        self.page = page
        self.url_esperada = "**/dashboard"

        # Elementos da tela de dashboard (ex: título ou indicador de saldo/sessão)
        self.titulo_dashboard = page.locator("h1, h2", has_text="Meu Caixa")
        self.botao_logout = page.locator("#logout, text=Sair")

    def validar_redirecionamento_com_sucesso(self):
        """Valida se a URL atual é a do dashboard e se o elemento principal está visível."""
        self.page.wait_for_url(self.url_esperada, timeout=5000)
        self.titulo_dashboard.wait_for(state="visible", timeout=5000)
        return "/dashboard" in self.page.url