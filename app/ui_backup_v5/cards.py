import customtkinter as ctk

from .theme import BORDA, CARD, TEXTO, TEXTO_SECUNDARIO


class CardContador(ctk.CTkFrame):
    def __init__(self, master, titulo: str, valor: str, destaque: str):
        super().__init__(
            master,
            fg_color=CARD,
            corner_radius=14,
            border_width=1,
            border_color=BORDA,
        )
        self.grid_columnconfigure(0, weight=1)

        self.titulo = ctk.CTkLabel(
            self,
            text=titulo,
            text_color=TEXTO_SECUNDARIO,
            font=ctk.CTkFont(size=10, weight="bold"),
        )
        self.titulo.grid(row=0, column=0, padx=14, pady=(13, 0), sticky="w")

        self.valor = ctk.CTkLabel(
            self,
            text=valor,
            text_color=destaque,
            font=ctk.CTkFont(size=27, weight="bold"),
        )
        self.valor.grid(row=1, column=0, padx=14, pady=(0, 12), sticky="w")
