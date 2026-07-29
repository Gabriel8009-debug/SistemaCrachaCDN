from pathlib import Path
import threading
from tkinter import messagebox

import customtkinter as ctk

from app.printer_service import imprimir_cracha
from .theme import AMARELO, AZUL, CARD, FUNDO, TEXTO, TEXTO_SECUNDARIO


class ReimpressaoPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=FUNDO)

        self.base_dir = Path(__file__).resolve().parents[2]
        self.output_dir = self.base_dir / "output"
        self.resultados: list[Path] = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)

        titulo = ctk.CTkLabel(
            self,
            text="Reimpressão",
            text_color=TEXTO,
            font=ctk.CTkFont(size=28, weight="bold"),
        )
        titulo.grid(row=0, column=0, padx=28, pady=(28, 4), sticky="w")

        subtitulo = ctk.CTkLabel(
            self,
            text="Localize um crachá já gerado e envie-o novamente para a impressora.",
            text_color=TEXTO_SECUNDARIO,
            font=ctk.CTkFont(size=14),
        )
        subtitulo.grid(row=1, column=0, padx=28, pady=(0, 18), sticky="w")

        busca = ctk.CTkFrame(self, fg_color=CARD, corner_radius=14)
        busca.grid(row=2, column=0, padx=28, pady=8, sticky="ew")
        busca.grid_columnconfigure(0, weight=1)

        self.campo = ctk.CTkEntry(
            busca,
            placeholder_text="Digite o nome ou número da linha",
            height=42,
        )
        self.campo.grid(row=0, column=0, padx=(16, 8), pady=16, sticky="ew")
        self.campo.bind("<Return>", lambda _: self.buscar())

        botao = ctk.CTkButton(
            busca,
            text="BUSCAR",
            height=42,
            fg_color=AMARELO,
            hover_color="#E49B0F",
            text_color=AZUL,
            font=ctk.CTkFont(weight="bold"),
            command=self.buscar,
        )
        botao.grid(row=0, column=1, padx=(8, 16), pady=16)

        self.resumo = ctk.CTkLabel(
            self,
            text="Nenhuma busca realizada.",
            text_color=TEXTO_SECUNDARIO,
        )
        self.resumo.grid(row=3, column=0, padx=28, pady=(8, 4), sticky="w")

        self.lista = ctk.CTkScrollableFrame(self, fg_color=CARD, corner_radius=14)
        self.lista.grid(row=4, column=0, padx=28, pady=(8, 28), sticky="nsew")
        self.lista.grid_columnconfigure(0, weight=1)

    def buscar(self):
        termo = self.campo.get().strip().lower()

        for widget in self.lista.winfo_children():
            widget.destroy()

        arquivos = list(self.output_dir.rglob("cracha_*.png")) if self.output_dir.exists() else []

        if termo:
            self.resultados = [
                arquivo for arquivo in arquivos
                if termo in arquivo.stem.lower().replace("_", " ")
            ]
        else:
            self.resultados = arquivos[-50:]

        self.resultados.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        self.resumo.configure(text=f"{len(self.resultados)} resultado(s) encontrado(s).")

        for indice, arquivo in enumerate(self.resultados):
            linha = ctk.CTkFrame(self.lista, fg_color="#F8FAFC", corner_radius=10)
            linha.grid(row=indice, column=0, padx=8, pady=6, sticky="ew")
            linha.grid_columnconfigure(0, weight=1)

            nome = arquivo.stem.split("_", 2)[-1].replace("_", " ").title()
            texto = ctk.CTkLabel(
                linha,
                text=f"{nome}\n{arquivo.parent.name}",
                justify="left",
                text_color=TEXTO,
                font=ctk.CTkFont(size=13, weight="bold"),
            )
            texto.grid(row=0, column=0, padx=14, pady=12, sticky="w")

            botao = ctk.CTkButton(
                linha,
                text="REIMPRIMIR",
                width=110,
                fg_color=AZUL,
                hover_color="#123B68",
                command=lambda caminho=arquivo: self.reimprimir(caminho),
            )
            botao.grid(row=0, column=1, padx=12, pady=10)

    def reimprimir(self, arquivo: Path):
        confirmar = messagebox.askyesno(
            "Confirmar reimpressão",
            f"Deseja reimprimir o arquivo?\n\n{arquivo.name}",
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
