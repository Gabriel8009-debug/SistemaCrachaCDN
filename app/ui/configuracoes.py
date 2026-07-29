import customtkinter as ctk

from app.path_manager import OUTPUT, TEMPLATES

from .theme import AMARELO, AZUL, BORDA, CARD, FUNDO, SUCESSO, TEXTO, TEXTO_SECUNDARIO


class ConfiguracoesPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=FUNDO)

        self.grid_columnconfigure((0, 1), weight=1)

        titulo = ctk.CTkLabel(
            self,
            text="Configurações",
            text_color=TEXTO,
            font=ctk.CTkFont(size=29, weight="bold"),
        )
        titulo.grid(
            row=0,
            column=0,
            columnspan=2,
            padx=30,
            pady=(28, 3),
            sticky="w",
        )

        subtitulo = ctk.CTkLabel(
            self,
            text="Visão geral da instalação e dos serviços utilizados.",
            text_color=TEXTO_SECUNDARIO,
            font=ctk.CTkFont(size=14),
        )
        subtitulo.grid(
            row=1,
            column=0,
            columnspan=2,
            padx=30,
            pady=(0, 18),
            sticky="w",
        )

        itens = [
            ("Impressora", "IDP CUBO1", "Configurada"),
            ("Google Sheets", "Pedidos de crachá", "Integrado"),
            ("Google Drive", "Fotos dos corretores", "Integrado"),
            ("Pasta de saída", str(OUTPUT), "Disponível"),
            ("Template", str(TEMPLATES / "corretor.png"), "Configurado"),
            ("Identidade visual", "#00244C  •  #FCAF17", "Oficial CDN"),
        ]

        for indice, (nome, valor, status) in enumerate(itens):
            coluna = indice % 2
            linha = 2 + indice // 2

            card = ctk.CTkFrame(
                self,
                fg_color=CARD,
                corner_radius=15,
                border_width=1,
                border_color=BORDA,
            )
            card.grid(
                row=linha,
                column=coluna,
                padx=(30 if coluna == 0 else 8, 8 if coluna == 0 else 30),
                pady=8,
                sticky="nsew",
            )
            card.grid_columnconfigure(0, weight=1)

            rotulo = ctk.CTkLabel(
                card,
                text=nome,
                text_color=TEXTO,
                font=ctk.CTkFont(size=14, weight="bold"),
            )
            rotulo.grid(
                row=0,
                column=0,
                padx=18,
                pady=(17, 3),
                sticky="w",
            )

            conteudo = ctk.CTkLabel(
                card,
                text=valor,
                text_color=TEXTO_SECUNDARIO,
                font=ctk.CTkFont(size=12),
                wraplength=360,
                justify="left",
            )
            conteudo.grid(
                row=1,
                column=0,
                padx=18,
                pady=(0, 10),
                sticky="w",
            )

            estado = ctk.CTkLabel(
                card,
                text=f"●  {status}",
                text_color=SUCESSO,
                font=ctk.CTkFont(size=11, weight="bold"),
            )
            estado.grid(
                row=2,
                column=0,
                padx=18,
                pady=(0, 17),
                sticky="w",
            )
