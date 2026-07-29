import customtkinter as ctk

from .theme import AMARELO, AZUL, SIDEBAR_LARGURA


class Sidebar(ctk.CTkFrame):
    def __init__(self, master, ao_navegar):
        super().__init__(
            master,
            width=SIDEBAR_LARGURA,
            corner_radius=0,
            fg_color=AZUL,
        )
        self.ao_navegar = ao_navegar
        self.botoes = {}

        self.grid_propagate(False)
        self.grid_rowconfigure(8, weight=1)

        marca = ctk.CTkLabel(
            self,
            text="CASA DE\nNEGÓCIOS",
            text_color="white",
            font=ctk.CTkFont(size=23, weight="bold"),
            justify="left",
        )
        marca.grid(row=0, column=0, padx=24, pady=(28, 6), sticky="w")

        sistema = ctk.CTkLabel(
            self,
            text="Sistema de Crachás",
            text_color=AMARELO,
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        sistema.grid(row=1, column=0, padx=24, pady=(0, 28), sticky="w")

        itens = [
            ("dashboard", "Dashboard"),
            ("producao", "Produzir crachás"),
            ("reimpressao", "Reimpressão"),
            ("historico", "Histórico"),
            ("configuracoes", "Configurações"),
        ]

        for indice, (chave, texto) in enumerate(itens, start=2):
            botao = ctk.CTkButton(
                self,
                text=texto,
                anchor="w",
                height=42,
                corner_radius=8,
                fg_color="transparent",
                hover_color="#123B68",
                text_color="white",
                font=ctk.CTkFont(size=14, weight="bold"),
                command=lambda pagina=chave: self.selecionar(pagina),
            )
            botao.grid(
                row=indice,
                column=0,
                padx=14,
                pady=4,
                sticky="ew",
            )
            self.botoes[chave] = botao

        rodape = ctk.CTkLabel(
            self,
            text="CDN • Operação interna",
            text_color="#B8C7D9",
            font=ctk.CTkFont(size=11),
        )
        rodape.grid(row=9, column=0, padx=24, pady=22, sticky="sw")

    def selecionar(self, pagina: str):
        for chave, botao in self.botoes.items():
            ativo = chave == pagina
            botao.configure(
                fg_color=AMARELO if ativo else "transparent",
                text_color=AZUL if ativo else "white",
                hover_color=AMARELO if ativo else "#123B68",
            )

        self.ao_navegar(pagina)
