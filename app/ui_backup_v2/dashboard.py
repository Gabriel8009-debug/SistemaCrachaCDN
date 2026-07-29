from datetime import datetime
from pathlib import Path

import customtkinter as ctk

from .cards import CardMetrica
from .theme import AMARELO, AZUL, CARD, FUNDO, SUCESSO, TEXTO, TEXTO_SECUNDARIO


class DashboardPage(ctk.CTkFrame):
    def __init__(self, master, ao_produzir):
        super().__init__(master, fg_color=FUNDO)
        self.ao_produzir = ao_produzir
        self.base_dir = Path(__file__).resolve().parents[2]
        self.output_dir = self.base_dir / "output"

        self.grid_columnconfigure((0, 1, 2, 3), weight=1)

        titulo = ctk.CTkLabel(
            self,
            text="Dashboard",
            text_color=TEXTO,
            font=ctk.CTkFont(size=28, weight="bold"),
        )
        titulo.grid(row=0, column=0, columnspan=4, padx=28, pady=(28, 4), sticky="w")

        subtitulo = ctk.CTkLabel(
            self,
            text="Visão geral da produção de crachás.",
            text_color=TEXTO_SECUNDARIO,
            font=ctk.CTkFont(size=14),
        )
        subtitulo.grid(row=1, column=0, columnspan=4, padx=28, pady=(0, 22), sticky="w")

        self.card_hoje = CardMetrica(self, "Produzidos hoje", "0", AMARELO)
        self.card_hoje.grid(row=2, column=0, padx=(28, 8), pady=8, sticky="ew")

        self.card_total = CardMetrica(self, "Total no output", "0", AZUL)
        self.card_total.grid(row=2, column=1, padx=8, pady=8, sticky="ew")

        self.card_status = CardMetrica(self, "Status", "Pronto", SUCESSO)
        self.card_status.grid(row=2, column=2, padx=8, pady=8, sticky="ew")

        self.card_data = CardMetrica(self, "Data", datetime.now().strftime("%d/%m"), AMARELO)
        self.card_data.grid(row=2, column=3, padx=(8, 28), pady=8, sticky="ew")

        destaque = ctk.CTkFrame(
            self,
            fg_color=CARD,
            corner_radius=16,
            border_width=1,
            border_color="#E4E7EC",
        )
        destaque.grid(row=3, column=0, columnspan=4, padx=28, pady=(18, 10), sticky="ew")
        destaque.grid_columnconfigure(0, weight=1)

        texto = ctk.CTkLabel(
            destaque,
            text="Pronto para produzir novos crachás?",
            text_color=TEXTO,
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        texto.grid(row=0, column=0, padx=24, pady=(23, 5), sticky="w")

        apoio = ctk.CTkLabel(
            destaque,
            text="O sistema buscará os pedidos pendentes no Google Sheets.",
            text_color=TEXTO_SECUNDARIO,
            font=ctk.CTkFont(size=13),
        )
        apoio.grid(row=1, column=0, padx=24, pady=(0, 24), sticky="w")

        botao = ctk.CTkButton(
            destaque,
            text="PRODUZIR CRACHÁS",
            height=46,
            corner_radius=10,
            fg_color=AMARELO,
            hover_color="#E49B0F",
            text_color=AZUL,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.ao_produzir,
        )
        botao.grid(row=0, column=1, rowspan=2, padx=24, pady=24)

        self.atualizar_metricas()

    def atualizar_metricas(self):
        arquivos = list(self.output_dir.rglob("cracha_*.png")) if self.output_dir.exists() else []
        hoje = datetime.now().strftime("%Y-%m-%d")
        produzidos_hoje = [
            arquivo
            for arquivo in arquivos
            if hoje in str(arquivo.parent)
        ]

        self.card_hoje.valor.configure(text=str(len(produzidos_hoje)))
        self.card_total.valor.configure(text=str(len(arquivos)))
