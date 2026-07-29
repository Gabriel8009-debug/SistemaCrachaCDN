from pathlib import Path
import threading
from tkinter import messagebox

import customtkinter as ctk
from PIL import Image

from app.printer_service import imprimir_cracha
from app.path_manager import OUTPUT

from .theme import (
    AMARELO,
    AMARELO_HOVER,
    AZUL,
    BORDA,
    CARD,
    FUNDO,
    TEXTO,
    TEXTO_SECUNDARIO,
)


class ReimpressaoPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=FUNDO)

        self.output_dir = OUTPUT
        self.resultados: list[Path] = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)

        titulo = ctk.CTkLabel(
            self,
            text="Reimpressão",
            text_color=TEXTO,
            font=ctk.CTkFont(size=29, weight="bold"),
        )
        titulo.grid(
            row=0,
            column=0,
            padx=30,
            pady=(28, 3),
            sticky="w",
        )

        subtitulo = ctk.CTkLabel(
            self,
            text="Pesquise, visualize e reimprima um crachá já produzido.",
            text_color=TEXTO_SECUNDARIO,
            font=ctk.CTkFont(size=14),
        )
        subtitulo.grid(
            row=1,
            column=0,
            padx=30,
            pady=(0, 18),
            sticky="w",
        )

        busca = ctk.CTkFrame(
            self,
            fg_color=CARD,
            corner_radius=15,
            border_width=1,
            border_color=BORDA,
        )
        busca.grid(
            row=2,
            column=0,
            padx=30,
            pady=7,
            sticky="ew",
        )
        busca.grid_columnconfigure(0, weight=1)

        self.campo = ctk.CTkEntry(
            busca,
            placeholder_text="Digite o nome ou o número da linha",
            height=44,
            border_color=BORDA,
        )
        self.campo.grid(
            row=0,
            column=0,
            padx=(16, 8),
            pady=16,
            sticky="ew",
        )
        self.campo.bind("<Return>", lambda _: self.buscar())

        botao = ctk.CTkButton(
            busca,
            text="BUSCAR",
            height=44,
            width=120,
            corner_radius=10,
            fg_color=AMARELO,
            hover_color=AMARELO_HOVER,
            text_color=AZUL,
            font=ctk.CTkFont(weight="bold"),
            command=self.buscar,
        )
        botao.grid(
            row=0,
            column=1,
            padx=(8, 16),
            pady=16,
        )

        self.resumo = ctk.CTkLabel(
            self,
            text="Digite um nome para localizar o crachá.",
            text_color=TEXTO_SECUNDARIO,
        )
        self.resumo.grid(
            row=3,
            column=0,
            padx=30,
            pady=(8, 4),
            sticky="w",
        )

        self.lista = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
        )
        self.lista.grid(
            row=4,
            column=0,
            padx=24,
            pady=(6, 24),
            sticky="nsew",
        )
        self.lista.grid_columnconfigure((0, 1), weight=1)

    def buscar(self):
        termo = self.campo.get().strip().lower()

        for widget in self.lista.winfo_children():
            widget.destroy()

        arquivos = (
            list(self.output_dir.rglob("cracha_*.png"))
            if self.output_dir.exists()
            else []
        )

        if termo:
            self.resultados = [
                arquivo
                for arquivo in arquivos
                if termo in arquivo.stem.lower().replace("_", " ")
            ]
        else:
            self.resultados = arquivos

        self.resultados.sort(
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )

        self.resumo.configure(
            text=f"{len(self.resultados)} resultado(s) encontrado(s)."
        )

        for indice, arquivo in enumerate(self.resultados[:50]):
            coluna = indice % 2
            linha_grid = indice // 2

            card = ctk.CTkFrame(
                self.lista,
                fg_color=CARD,
                corner_radius=15,
                border_width=1,
                border_color=BORDA,
            )
            card.grid(
                row=linha_grid,
                column=coluna,
                padx=7,
                pady=7,
                sticky="nsew",
            )
            card.grid_columnconfigure(1, weight=1)

            try:
                imagem = Image.open(arquivo)
                miniatura = ctk.CTkImage(
                    light_image=imagem,
                    dark_image=imagem,
                    size=(92, 147),
                )
                preview = ctk.CTkLabel(
                    card,
                    text="",
                    image=miniatura,
                )
                preview.image = miniatura
            except Exception:
                preview = ctk.CTkLabel(
                    card,
                    text="SEM\nPRÉVIA",
                    width=92,
                    height=147,
                    fg_color="#EEF2F6",
                    corner_radius=8,
                    text_color=TEXTO_SECUNDARIO,
                )

            preview.grid(
                row=0,
                column=0,
                rowspan=3,
                padx=14,
                pady=14,
            )

            nome = (
                arquivo.stem
                .split("_", 2)[-1]
                .replace("_", " ")
                .title()
            )

            nome_label = ctk.CTkLabel(
                card,
                text=nome,
                text_color=TEXTO,
                font=ctk.CTkFont(size=14, weight="bold"),
                wraplength=190,
                justify="left",
            )
            nome_label.grid(
                row=0,
                column=1,
                padx=(0, 14),
                pady=(18, 2),
                sticky="nw",
            )

            data = ctk.CTkLabel(
                card,
                text=f"Gerado em {arquivo.parent.name}",
                text_color=TEXTO_SECUNDARIO,
                font=ctk.CTkFont(size=11),
            )
            data.grid(
                row=1,
                column=1,
                padx=(0, 14),
                pady=(0, 8),
                sticky="nw",
            )

            botao = ctk.CTkButton(
                card,
                text="REIMPRIMIR",
                height=36,
                fg_color=AZUL,
                hover_color="#123B68",
                font=ctk.CTkFont(size=12, weight="bold"),
                command=lambda caminho=arquivo: self.reimprimir(caminho),
            )
            botao.grid(
                row=2,
                column=1,
                padx=(0, 14),
                pady=(0, 16),
                sticky="ew",
            )

    def reimprimir(self, arquivo: Path):
        confirmar = messagebox.askyesno(
            "Confirmar reimpressão",
            f"Deseja reimprimir este crachá?\n\n{arquivo.name}",
        )
        if not confirmar:
            return

        threading.Thread(
            target=self._executar_reimpressao,
            args=(arquivo,),
            daemon=True,
        ).start()

    def _executar_reimpressao(self, arquivo: Path):
        try:
            imprimir_cracha(arquivo)
            self.after(
                0,
                lambda: messagebox.showinfo(
                    "Reimpressão",
                    "Crachá enviado para a impressora.",
                ),
            )
        except Exception as erro:
            self.after(
                0,
                lambda: messagebox.showerror(
                    "Erro",
                    f"Não foi possível reimprimir:\n\n{erro}",
                ),
            )
