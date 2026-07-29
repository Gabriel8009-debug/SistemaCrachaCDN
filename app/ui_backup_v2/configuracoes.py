from pathlib import Path

import customtkinter as ctk

from .theme import AMARELO, AZUL, CARD, FUNDO, TEXTO, TEXTO_SECUNDARIO


class ConfiguracoesPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=FUNDO)

        base_dir = Path(__file__).resolve().parents[2]

        self.grid_columnconfigure(0, weight=1)

        titulo = ctk.CTkLabel(
            self,
            text="Configurações",
            text_color=TEXTO,
            font=ctk.CTkFont(size=28, weight="bold"),
        )
        titulo.grid(row=0, column=0, padx=28, pady=(28, 4), sticky="w")

        subtitulo = ctk.CTkLabel(
            self,
            text="Informações principais da instalação atual.",
            text_color=TEXTO_SECUNDARIO,
            font=ctk.CTkFont(size=14),
        )
        subtitulo.grid(row=1, column=0, padx=28, pady=(0, 18), sticky="w")

        itens = [
            ("Impressora", "IDP CUBO1"),
            ("Pasta do sistema", str(base_dir)),
            ("Pasta de saída", str(base_dir / "output")),
            ("Template", str(base_dir / "templates" / "corretor.png")),
            ("Cor azul", "#00244C"),
            ("Cor amarela", "#FCAF17"),
        ]

        card = ctk.CTkFrame(
            self,
            fg_color=CARD,
            corner_radius=14,
            border_width=1,
            border_color="#E4E7EC",
        )
        card.grid(row=2, column=0, padx=28, pady=10, sticky="ew")
        card.grid_columnconfigure(1, weight=1)

        for linha, (nome, valor) in enumerate(itens):
            rotulo = ctk.CTkLabel(
                card,
                text=nome,
                text_color=TEXTO,
                font=ctk.CTkFont(size=13, weight="bold"),
            )
            rotulo.grid(row=linha, column=0, padx=18, pady=13, sticky="w")

            conteudo = ctk.CTkLabel(
                card,
                text=valor,
                text_color=TEXTO_SECUNDARIO,
                anchor="w",
            )
            conteudo.grid(row=linha, column=1, padx=18, pady=13, sticky="ew")
