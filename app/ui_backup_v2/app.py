import customtkinter as ctk

from .configuracoes import ConfiguracoesPage
from .dashboard import DashboardPage
from .historico import HistoricoPage
from .producao import ProducaoPage
from .reimpressao import ReimpressaoPage
from .sidebar import Sidebar
from .theme import FUNDO, SIDEBAR_LARGURA


class SistemaCrachaApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("light")

        self.title("Sistema de Crachás CDN")
        self.geometry("1180x720")
        self.minsize(1020, 640)
        self.configure(fg_color=FUNDO)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.sidebar = Sidebar(self, self.mostrar_pagina)
        self.sidebar.grid(row=0, column=0, sticky="nsw")

        self.conteudo = ctk.CTkFrame(
            self,
            fg_color=FUNDO,
            corner_radius=0,
        )
        self.conteudo.grid(row=0, column=1, sticky="nsew")
        self.conteudo.grid_rowconfigure(0, weight=1)
        self.conteudo.grid_columnconfigure(0, weight=1)

        self.paginas = {
            "dashboard": DashboardPage(
                self.conteudo,
                ao_produzir=lambda: self.sidebar.selecionar("producao"),
            ),
            "producao": ProducaoPage(self.conteudo),
            "reimpressao": ReimpressaoPage(self.conteudo),
            "historico": HistoricoPage(self.conteudo),
            "configuracoes": ConfiguracoesPage(self.conteudo),
        }

        for pagina in self.paginas.values():
            pagina.grid(row=0, column=0, sticky="nsew")

        self.sidebar.selecionar("dashboard")

    def mostrar_pagina(self, nome: str):
        pagina = self.paginas[nome]

        if nome == "dashboard":
            pagina.atualizar_metricas()
        elif nome == "historico":
            pagina.carregar()

        pagina.tkraise()


def iniciar_interface():
    app = SistemaCrachaApp()
    app.mainloop()
