import customtkinter as ctk

from .theme import CARD, TEXTO, TEXTO_SECUNDARIO


class CardMetrica(ctk.CTkFrame):
    def __init__(self, master, titulo: str, valor: str, destaque: str):
        super().__init__(
            master,
            fg_color=CARD,
            corner_radius=14,
            border_width=1,
            border_color="#E4E7EC",
        )

        self.grid_columnconfigure(0, weight=1)

        faixa = ctk.CTkFrame(
            self,
            width=6,
            corner_radius=6,
            fg_color=destaque,
        )
        faixa.grid(row=0, column=0, rowspan=2, sticky="nsw", padx=(0, 12))

        self.titulo = ctk.CTkLabel(
            self,
            text=titulo,
            text_color=TEXTO_SECUNDARIO,
            font=ctk.CTkFont(size=13),
        )
        self.titulo.grid(row=0, column=1, padx=(0, 18), pady=(15, 2), sticky="w")

        self.valor = ctk.CTkLabel(
            self,
            text=valor,
            text_color=TEXTO,
            font=ctk.CTkFont(size=28, weight="bold"),
        )
        self.valor.grid(row=1, column=1, padx=(0, 18), pady=(0, 15), sticky="w")
