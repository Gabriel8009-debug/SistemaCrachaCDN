from datetime import datetime
from pathlib import Path

import customtkinter as ctk

from .theme import (
    AMARELO,
    AMARELO_HOVER,
    AZUL,
    BORDA,
    CARD,
    FUNDO,
    SUCESSO,
    TEXTO,
    TEXTO_SECUNDARIO,
)


class DashboardPage(ctk.CTkFrame):
    def __init__(self, master, ao_produzir):
        super().__init__(master, fg_color=FUNDO)

        self.ao_produzir = ao_produzir
        self.base_dir = Path(__file__).resolve().parents[2]
        self.output_dir = self.base_dir / "output"

        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(3, weight=1)

        titulo = ctk.CTkLabel(
            self,
            text="Sistema de Crachás",
            text_color=TEXTO,
            font=ctk.CTkFont(size=30, weight="bold"),
        )
        titulo.grid(row=0, column=0, columnspan=2, padx=30, pady=(28, 3), sticky="w")

        subtitulo = ctk.CTkLabel(
            self,
            text="Central de produção e controle operacional.",
            text_color=TEXTO_SECUNDARIO,
            font=ctk.CTkFont(size=14),
        )
        subtitulo.grid(row=1, column=0, columnspan=2, padx=30, pady=(0, 20), sticky="w")

        principal = ctk.CTkFrame(
            self,
            fg_color=AZUL,
            corner_radius=18,
        )
        principal.grid(row=2, column=0, padx=(30, 10), pady=8, sticky="nsew")
        principal.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            principal,
            text="PRONTO PARA PRODUZIR",
            text_color=AMARELO,
            font=ctk.CTkFont(size=11, weight="bold"),
        ).grid(row=0, column=0, padx=24, pady=(26, 6), sticky="w")

        ctk.CTkLabel(
            principal,
            text="Inicie o processamento dos\npedidos pendentes",
            justify="left",
            text_color="white",
            font=ctk.CTkFont(size=28, weight="bold"),
        ).grid(row=1, column=0, padx=24, pady=(0, 8), sticky="w")

        ctk.CTkLabel(
            principal,
            text="O sistema buscará os pedidos, tratará as imagens,\ngerará os crachás e solicitará a confirmação antes da impressão.",
            justify="left",
            text_color="#D7E1EC",
            font=ctk.CTkFont(size=13),
        ).grid(row=2, column=0, padx=24, pady=(0, 22), sticky="w")

        ctk.CTkButton(
            principal,
            text="▶  PRODUZIR CRACHÁS",
            height=52,
            corner_radius=11,
            fg_color=AMARELO,
            hover_color=AMARELO_HOVER,
            text_color=AZUL,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.ao_produzir,
        ).grid(row=3, column=0, padx=24, pady=(0, 26), sticky="w")

        status = ctk.CTkFrame(
            self,
            fg_color=CARD,
            corner_radius=18,
            border_width=1,
            border_color=BORDA,
        )
        status.grid(row=2, column=1, padx=(10, 30), pady=8, sticky="nsew")
        status.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            status,
            text="STATUS DOS SERVIÇOS",
            text_color=TEXTO_SECUNDARIO,
            font=ctk.CTkFont(size=11, weight="bold"),
        ).grid(row=0, column=0, padx=20, pady=(22, 12), sticky="w")

        for indice, (nome, detalhe) in enumerate([
            ("Google Sheets", "Conectado"),
            ("Google Drive", "Conectado"),
            ("Impressora", "Disponível"),
        ], start=1):
            linha = ctk.CTkFrame(status, fg_color="#F8FAFC", corner_radius=10)
            linha.grid(row=indice, column=0, padx=18, pady=5, sticky="ew")
            linha.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(
                linha,
                text="●",
                text_color=SUCESSO,
                font=ctk.CTkFont(size=16),
            ).grid(row=0, column=0, padx=(12, 8), pady=11)

            ctk.CTkLabel(
                linha,
                text=nome,
                text_color=TEXTO,
                font=ctk.CTkFont(size=12, weight="bold"),
            ).grid(row=0, column=1, pady=11, sticky="w")

            ctk.CTkLabel(
                linha,
                text=detalhe,
                text_color=TEXTO_SECUNDARIO,
                font=ctk.CTkFont(size=11),
            ).grid(row=0, column=2, padx=12, pady=11)

        self.resumo = ctk.CTkLabel(
            status,
            text="",
            text_color=TEXTO_SECUNDARIO,
            font=ctk.CTkFont(size=11),
        )
        self.resumo.grid(row=5, column=0, padx=20, pady=(12, 20), sticky="w")

        recentes = ctk.CTkFrame(
            self,
            fg_color=CARD,
            corner_radius=18,
            border_width=1,
            border_color=BORDA,
        )
        recentes.grid(row=3, column=0, columnspan=2, padx=30, pady=(10, 30), sticky="nsew")
        recentes.grid_columnconfigure(0, weight=1)
        recentes.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            recentes,
            text="Últimos produzidos",
            text_color=TEXTO,
            font=ctk.CTkFont(size=17, weight="bold"),
        ).grid(row=0, column=0, padx=20, pady=(18, 10), sticky="w")

        self.lista_recentes = ctk.CTkScrollableFrame(
            recentes,
            fg_color="transparent",
        )
        self.lista_recentes.grid(row=1, column=0, padx=14, pady=(0, 14), sticky="nsew")
        self.lista_recentes.grid_columnconfigure(0, weight=1)

        self.atualizar_metricas()

    def atualizar_metricas(self):
        arquivos = list(self.output_dir.rglob("cracha_*.png")) if self.output_dir.exists() else []
        hoje = datetime.now().strftime("%Y-%m-%d")
        produzidos_hoje = [a for a in arquivos if hoje in str(a.parent)]

        self.resumo.configure(
            text=f"{len(produzidos_hoje)} produzidos hoje  •  {len(arquivos)} no sistema"
        )

        for widget in self.lista_recentes.winfo_children():
            widget.destroy()

        recentes = sorted(arquivos, key=lambda p: p.stat().st_mtime, reverse=True)[:8]

        if not recentes:
            ctk.CTkLabel(
                self.lista_recentes,
                text="Nenhum crachá encontrado.",
                text_color=TEXTO_SECUNDARIO,
            ).grid(row=0, column=0, pady=20)
            return

        for indice, arquivo in enumerate(recentes):
            linha = ctk.CTkFrame(self.lista_recentes, fg_color="#F8FAFC", corner_radius=10)
            linha.grid(row=indice, column=0, padx=4, pady=4, sticky="ew")
            linha.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(
                linha,
                text="▣",
                width=34,
                height=34,
                corner_radius=8,
                fg_color="#FFF3D1",
                text_color=AMARELO,
                font=ctk.CTkFont(size=17, weight="bold"),
            ).grid(row=0, column=0, rowspan=2, padx=(12, 10), pady=9)

            nome = arquivo.stem.split("_", 2)[-1].replace("_", " ").title()
            ctk.CTkLabel(
                linha,
                text=nome,
                text_color=TEXTO,
                font=ctk.CTkFont(size=13, weight="bold"),
            ).grid(row=0, column=1, padx=(0, 12), pady=(9, 0), sticky="w")

            ctk.CTkLabel(
                linha,
                text="Produzido",
                text_color=SUCESSO,
                font=ctk.CTkFont(size=11, weight="bold"),
            ).grid(row=1, column=1, padx=(0, 12), pady=(0, 9), sticky="w")

            horario = datetime.fromtimestamp(arquivo.stat().st_mtime).strftime("%d/%m/%Y • %H:%M")
            ctk.CTkLabel(
                linha,
                text=horario,
                text_color=TEXTO_SECUNDARIO,
                font=ctk.CTkFont(size=11),
            ).grid(row=0, column=2, rowspan=2, padx=14, pady=11)
