from datetime import datetime
from pathlib import Path

import customtkinter as ctk

from .theme import CARD, FUNDO, TEXTO, TEXTO_SECUNDARIO


class HistoricoPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=FUNDO)

        self.base_dir = Path(__file__).resolve().parents[2]
        self.output_dir = self.base_dir / "output"

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        titulo = ctk.CTkLabel(
            self,
            text="Histórico",
            text_color=TEXTO,
            font=ctk.CTkFont(size=28, weight="bold"),
        )
        titulo.grid(row=0, column=0, padx=28, pady=(28, 4), sticky="w")

        subtitulo = ctk.CTkLabel(
            self,
            text="Arquivos de crachá encontrados na pasta de saída.",
            text_color=TEXTO_SECUNDARIO,
            font=ctk.CTkFont(size=14),
        )
        subtitulo.grid(row=1, column=0, padx=28, pady=(0, 18), sticky="w")

        self.resumo = ctk.CTkLabel(
            self,
            text="",
            text_color=TEXTO_SECUNDARIO,
        )
        self.resumo.grid(row=2, column=0, padx=28, pady=4, sticky="w")

        self.lista = ctk.CTkScrollableFrame(self, fg_color=CARD, corner_radius=14)
        self.lista.grid(row=3, column=0, padx=28, pady=(8, 28), sticky="nsew")
        self.lista.grid_columnconfigure(1, weight=1)

        self.carregar()

    def carregar(self):
        for widget in self.lista.winfo_children():
            widget.destroy()

        arquivos = list(self.output_dir.rglob("cracha_*.png")) if self.output_dir.exists() else []
        arquivos.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        self.resumo.configure(text=f"{len(arquivos)} crachá(s) registrado(s).")

        cabecalhos = ["Data", "Nome", "Arquivo"]
        for coluna, texto in enumerate(cabecalhos):
            label = ctk.CTkLabel(
                self.lista,
                text=texto,
                text_color=TEXTO,
                font=ctk.CTkFont(size=12, weight="bold"),
            )
            label.grid(row=0, column=coluna, padx=12, pady=10, sticky="w")

        for linha, arquivo in enumerate(arquivos[:200], start=1):
            data = datetime.fromtimestamp(arquivo.stat().st_mtime).strftime("%d/%m/%Y %H:%M")
            nome = arquivo.stem.split("_", 2)[-1].replace("_", " ").title()

            valores = [data, nome, arquivo.name]
            for coluna, valor in enumerate(valores):
                label = ctk.CTkLabel(
                    self.lista,
                    text=valor,
                    text_color=TEXTO_SECUNDARIO,
                    anchor="w",
                )
                label.grid(row=linha, column=coluna, padx=12, pady=7, sticky="ew")
