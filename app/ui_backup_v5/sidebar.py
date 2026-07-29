import customtkinter as ctk

from .theme import AMARELO, AZUL, AZUL_2, SIDEBAR_LARGURA


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
        self.barras = {}

        self.grid_propagate(False)
        self.grid_rowconfigure(10, weight=1)
        self.grid_columnconfigure(0, weight=1)

        topo = ctk.CTkFrame(self, fg_color="transparent")
        topo.grid(row=0, column=0, padx=18, pady=(24, 18), sticky="ew")
        topo.grid_columnconfigure(1, weight=1)

        simbolo = ctk.CTkLabel(
            topo,
            text="CDN",
            width=58,
            height=50,
            corner_radius=12,
            fg_color=AMARELO,
            text_color=AZUL,
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        simbolo.grid(row=0, column=0, rowspan=2, padx=(0, 10))

        marca = ctk.CTkLabel(
            topo,
            text="CASA DE\nNEGÓCIOS",
            justify="left",
            text_color="white",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        marca.grid(row=0, column=1, sticky="sw")

        sistema = ctk.CTkLabel(
            topo,
            text="Sistema de Crachás",
            text_color="#AFC0D2",
            font=ctk.CTkFont(size=11),
        )
        sistema.grid(row=1, column=1, sticky="nw")

        divisor = ctk.CTkFrame(self, height=1, fg_color="#21486F")
        divisor.grid(row=1, column=0, padx=16, pady=(0, 12), sticky="ew")

        itens = [
            ("dashboard", "⌂", "Início"),
            ("producao", "▣", "Produção"),
            ("reimpressao", "↻", "Reimpressão"),
            ("historico", "≡", "Histórico"),
            ("configuracoes", "⚙", "Configurações"),
        ]

        for indice, (chave, icone, texto) in enumerate(itens, start=2):
            linha = ctk.CTkFrame(self, fg_color="transparent")
            linha.grid(row=indice, column=0, padx=8, pady=3, sticky="ew")
            linha.grid_columnconfigure(1, weight=1)

            barra = ctk.CTkFrame(
                linha,
                width=4,
                height=38,
                corner_radius=4,
                fg_color="transparent",
            )
            barra.grid(row=0, column=0, padx=(0, 5), pady=2)

            botao = ctk.CTkButton(
                linha,
                text=f"{icone}  {texto}",
                anchor="w",
                height=42,
                corner_radius=9,
                fg_color="transparent",
                hover_color=AZUL_2,
                text_color="white",
                font=ctk.CTkFont(size=13, weight="bold"),
                command=lambda pagina=chave: self.selecionar(pagina),
            )
            botao.grid(row=0, column=1, sticky="ew")

            self.botoes[chave] = botao
            self.barras[chave] = barra

        status = ctk.CTkFrame(self, fg_color=AZUL_2, corner_radius=12)
        status.grid(row=10, column=0, padx=12, pady=(12, 8), sticky="sew")
        status.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            status,
            text="●",
            text_color="#45D483",
            font=ctk.CTkFont(size=16),
        ).grid(row=0, column=0, padx=(12, 6), pady=11)

        ctk.CTkLabel(
            status,
            text="Sistema disponível",
            text_color="white",
            font=ctk.CTkFont(size=11, weight="bold"),
        ).grid(row=0, column=1, padx=(0, 8), pady=11, sticky="w")

        ctk.CTkLabel(
            self,
            text="Versão 5.0",
            text_color="#8EA6C0",
            font=ctk.CTkFont(size=10),
        ).grid(row=11, column=0, padx=18, pady=(2, 18), sticky="w")

    def selecionar(self, pagina: str):
        for chave, botao in self.botoes.items():
            ativo = chave == pagina
            botao.configure(
                fg_color=AZUL_2 if ativo else "transparent",
                text_color="white",
                hover_color=AZUL_2,
            )
            self.barras[chave].configure(
                fg_color=AMARELO if ativo else "transparent"
            )

        self.ao_navegar(pagina)
