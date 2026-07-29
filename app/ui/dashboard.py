from datetime import datetime
from pathlib import Path

import customtkinter as ctk
from PIL import Image

from app.path_manager import OUTPUT

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
        self.output_dir = OUTPUT
        self.icon_dir = Path(__file__).resolve().parent / "assets" / "icons"
        self.imagens = {}

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)

        ctk.CTkLabel(
            self,
            text="Sistema de Crachás",
            text_color=TEXTO,
            font=ctk.CTkFont(size=30, weight="bold"),
        ).grid(row=0, column=0, padx=30, pady=(28, 3), sticky="w")

        ctk.CTkLabel(
            self,
            text="Tudo pronto para iniciar uma nova produção.",
            text_color=TEXTO_SECUNDARIO,
            font=ctk.CTkFont(size=14),
        ).grid(row=1, column=0, padx=30, pady=(0, 18), sticky="w")

        status = ctk.CTkFrame(
            self,
            fg_color=CARD,
            corner_radius=18,
            border_width=1,
            border_color=BORDA,
        )
        status.grid(row=2, column=0, padx=30, pady=8, sticky="ew")
        status.grid_columnconfigure((0, 1, 2), weight=1)

        servicos = [
            ("sheet", "Google Sheets", "Conectado"),
            ("cloud", "Google Drive", "Conectado"),
            ("printer", "Impressora", "Disponível"),
        ]

        for coluna, (icone_nome, nome, detalhe) in enumerate(servicos):
            bloco = ctk.CTkFrame(status, fg_color="#F8FAFC", corner_radius=12)
            bloco.grid(
                row=0,
                column=coluna,
                padx=(16 if coluna == 0 else 6, 16 if coluna == 2 else 6),
                pady=16,
                sticky="ew",
            )
            bloco.grid_columnconfigure(1, weight=1)

            img = Image.open(self.icon_dir / f"{icone_nome}.png")
            icon = ctk.CTkImage(light_image=img, dark_image=img, size=(22, 22))
            self.imagens[icone_nome] = icon

            ctk.CTkLabel(
                bloco,
                text="",
                image=icon,
                width=42,
                height=42,
                corner_radius=10,
                fg_color="#EAF0F6",
            ).grid(row=0, column=0, rowspan=2, padx=10, pady=10)

            ctk.CTkLabel(
                bloco,
                text=nome,
                text_color=TEXTO,
                font=ctk.CTkFont(size=12, weight="bold"),
            ).grid(row=0, column=1, padx=(0, 10), pady=(10, 0), sticky="sw")

            ctk.CTkLabel(
                bloco,
                text=f"●  {detalhe}",
                text_color=SUCESSO,
                font=ctk.CTkFont(size=10, weight="bold"),
            ).grid(row=1, column=1, padx=(0, 10), pady=(0, 10), sticky="nw")

        principal = ctk.CTkFrame(
            self,
            fg_color=AZUL,
            corner_radius=20,
        )
        principal.grid(row=3, column=0, padx=30, pady=(10, 8), sticky="ew")
        principal.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            principal,
            text="PRONTO PARA PRODUZIR",
            text_color=AMARELO,
            font=ctk.CTkFont(size=11, weight="bold"),
        ).grid(row=0, column=0, padx=26, pady=(26, 5), sticky="w")

        ctk.CTkLabel(
            principal,
            text="Produza os crachás pendentes",
            text_color="white",
            font=ctk.CTkFont(size=27, weight="bold"),
        ).grid(row=1, column=0, padx=26, pady=(0, 4), sticky="w")

        ctk.CTkLabel(
            principal,
            text="Busca dos pedidos, tratamento das fotos, geração dos arquivos e confirmação de impressão.",
            text_color="#D7E1EC",
            font=ctk.CTkFont(size=13),
        ).grid(row=2, column=0, padx=26, pady=(0, 24), sticky="w")

        play_img = Image.open(self.icon_dir / "play.png")
        self.play_icon = ctk.CTkImage(
            light_image=play_img,
            dark_image=play_img,
            size=(18, 18),
        )

        ctk.CTkButton(
            principal,
            text="PRODUZIR CRACHÁS",
            image=self.play_icon,
            compound="left",
            height=52,
            corner_radius=11,
            fg_color=AMARELO,
            hover_color=AMARELO_HOVER,
            text_color=AZUL,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.ao_produzir,
        ).grid(row=0, column=1, rowspan=3, padx=26, pady=26)

        recentes = ctk.CTkFrame(
            self,
            fg_color=CARD,
            corner_radius=18,
            border_width=1,
            border_color=BORDA,
        )
        recentes.grid(row=4, column=0, padx=30, pady=(10, 30), sticky="nsew")
        recentes.grid_columnconfigure(0, weight=1)
        recentes.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            recentes,
            text="Últimos produzidos",
            text_color=TEXTO,
            font=ctk.CTkFont(size=17, weight="bold"),
        ).grid(row=0, column=0, padx=20, pady=(18, 10), sticky="w")

        self.lista_recentes = ctk.CTkScrollableFrame(recentes, fg_color="transparent")
        self.lista_recentes.grid(row=1, column=0, padx=14, pady=(0, 14), sticky="nsew")
        self.lista_recentes.grid_columnconfigure(0, weight=1)

        self.atualizar_metricas()

    def atualizar_metricas(self):
        arquivos = list(self.output_dir.rglob("cracha_*.png")) if self.output_dir.exists() else []

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

            nome = arquivo.stem.split("_", 2)[-1].replace("_", " ").title()
            horario = datetime.fromtimestamp(arquivo.stat().st_mtime).strftime("%d/%m/%Y • %H:%M")

            ctk.CTkLabel(
                linha,
                text="▣",
                width=36,
                height=36,
                corner_radius=8,
                fg_color="#FFF3D1",
                text_color=AMARELO,
                font=ctk.CTkFont(size=17, weight="bold"),
            ).grid(row=0, column=0, rowspan=2, padx=(12, 10), pady=9)

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

            ctk.CTkLabel(
                linha,
                text=horario,
                text_color=TEXTO_SECUNDARIO,
                font=ctk.CTkFont(size=11),
            ).grid(row=0, column=2, rowspan=2, padx=14, pady=11)
