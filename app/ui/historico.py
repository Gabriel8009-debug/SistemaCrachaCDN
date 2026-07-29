from datetime import datetime
from pathlib import Path

import customtkinter as ctk

from app.path_manager import OUTPUT

from .theme import AMARELO, BORDA, CARD, FUNDO, SUCESSO, TEXTO, TEXTO_SECUNDARIO


class HistoricoPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=FUNDO)

        self.output_dir = OUTPUT

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        ctk.CTkLabel(
            self,
            text="Histórico",
            text_color=TEXTO,
            font=ctk.CTkFont(size=29, weight="bold"),
        ).grid(row=0, column=0, padx=30, pady=(28, 3), sticky="w")

        ctk.CTkLabel(
            self,
            text="Visualize os crachás gerados em ordem cronológica.",
            text_color=TEXTO_SECUNDARIO,
            font=ctk.CTkFont(size=14),
        ).grid(row=1, column=0, padx=30, pady=(0, 18), sticky="w")

        self.resumo = ctk.CTkLabel(
            self,
            text="",
            text_color=TEXTO_SECUNDARIO,
        )
        self.resumo.grid(row=2, column=0, padx=30, pady=4, sticky="w")

        painel = ctk.CTkFrame(
            self,
            fg_color=CARD,
            corner_radius=16,
            border_width=1,
            border_color=BORDA,
        )
        painel.grid(row=3, column=0, padx=30, pady=(8, 30), sticky="nsew")
        painel.grid_columnconfigure(0, weight=1)
        painel.grid_rowconfigure(0, weight=1)

        self.lista = ctk.CTkScrollableFrame(
            painel,
            fg_color="transparent",
        )
        self.lista.grid(row=0, column=0, padx=12, pady=12, sticky="nsew")
        self.lista.grid_columnconfigure(0, weight=1)

        self.carregar()

    def carregar(self):
        for widget in self.lista.winfo_children():
            widget.destroy()

        arquivos = list(self.output_dir.rglob("cracha_*.png")) if self.output_dir.exists() else []
        arquivos.sort(key=lambda p: p.stat().st_mtime, reverse=True)

        self.resumo.configure(text=f"{len(arquivos)} crachá(s) registrado(s).")

        for linha_idx, arquivo in enumerate(arquivos[:300]):
            item = ctk.CTkFrame(
                self.lista,
                fg_color="#F8FAFC",
                corner_radius=11,
            )
            item.grid(row=linha_idx, column=0, padx=4, pady=4, sticky="ew")
            item.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(
                item,
                text="▣",
                width=38,
                height=38,
                corner_radius=9,
                fg_color="#FFF3D1",
                text_color=AMARELO,
                font=ctk.CTkFont(size=18, weight="bold"),
            ).grid(row=0, column=0, rowspan=2, padx=(12, 10), pady=10)

            nome = arquivo.stem.split("_", 2)[-1].replace("_", " ").title()
            ctk.CTkLabel(
                item,
                text=nome,
                text_color=TEXTO,
                font=ctk.CTkFont(size=13, weight="bold"),
            ).grid(row=0, column=1, padx=(0, 12), pady=(10, 0), sticky="w")

            ctk.CTkLabel(
                item,
                text=arquivo.name,
                text_color=TEXTO_SECUNDARIO,
                font=ctk.CTkFont(size=10),
            ).grid(row=1, column=1, padx=(0, 12), pady=(0, 10), sticky="w")

            data = datetime.fromtimestamp(arquivo.stat().st_mtime).strftime("%d/%m/%Y • %H:%M")
            ctk.CTkLabel(
                item,
                text=data,
                text_color=TEXTO_SECUNDARIO,
                font=ctk.CTkFont(size=11),
            ).grid(row=0, column=2, padx=12, pady=(10, 0), sticky="e")

            ctk.CTkLabel(
                item,
                text="●  Produzido",
                text_color=SUCESSO,
                font=ctk.CTkFont(size=10, weight="bold"),
            ).grid(row=1, column=2, padx=12, pady=(0, 10), sticky="e")
