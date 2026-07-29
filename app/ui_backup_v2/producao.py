import queue
import sys
import threading
from pathlib import Path
from tkinter import messagebox

import customtkinter as ctk

from app.processador_pedidos import processar_pedidos
from .theme import AMARELO, AZUL, CARD, ERRO, FUNDO, SUCESSO, TEXTO, TEXTO_SECUNDARIO


class SaidaInterface:
    def __init__(self, fila: queue.Queue[str]):
        self.fila = fila

    def write(self, texto: str) -> int:
        if texto:
            self.fila.put(texto)
        return len(texto)

    def flush(self):
        pass


class ProducaoPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=FUNDO)

        self.processando = False
        self.fila: queue.Queue[str] = queue.Queue()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(5, weight=1)

        titulo = ctk.CTkLabel(
            self,
            text="Produzir crachás",
            text_color=TEXTO,
            font=ctk.CTkFont(size=28, weight="bold"),
        )
        titulo.grid(row=0, column=0, padx=28, pady=(28, 4), sticky="w")

        subtitulo = ctk.CTkLabel(
            self,
            text="Busque os pedidos pendentes, gere os arquivos e confirme a impressão.",
            text_color=TEXTO_SECUNDARIO,
            font=ctk.CTkFont(size=14),
        )
        subtitulo.grid(row=1, column=0, padx=28, pady=(0, 18), sticky="w")

        painel_status = ctk.CTkFrame(
            self,
            fg_color=CARD,
            corner_radius=14,
            border_width=1,
            border_color="#E4E7EC",
        )
        painel_status.grid(row=2, column=0, padx=28, pady=8, sticky="ew")
        painel_status.grid_columnconfigure(1, weight=1)

        self.indicador = ctk.CTkLabel(
            painel_status,
            text="●",
            text_color=SUCESSO,
            font=ctk.CTkFont(size=22),
        )
        self.indicador.grid(row=0, column=0, padx=(20, 10), pady=18)

        self.status = ctk.CTkLabel(
            painel_status,
            text="Sistema pronto",
            text_color=TEXTO,
            font=ctk.CTkFont(size=15, weight="bold"),
        )
        self.status.grid(row=0, column=1, pady=18, sticky="w")

        self.botao = ctk.CTkButton(
            painel_status,
            text="INICIAR PROCESSAMENTO",
            height=42,
            corner_radius=9,
            fg_color=AMARELO,
            hover_color="#E49B0F",
            text_color=AZUL,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.iniciar,
        )
        self.botao.grid(row=0, column=2, padx=18, pady=14)

        self.progresso = ctk.CTkProgressBar(
            self,
            progress_color=AMARELO,
            fg_color="#DDE3EA",
            height=10,
        )
        self.progresso.grid(row=3, column=0, padx=28, pady=(12, 4), sticky="ew")
        self.progresso.set(0)

        self.texto_progresso = ctk.CTkLabel(
            self,
            text="Aguardando início",
            text_color=TEXTO_SECUNDARIO,
            font=ctk.CTkFont(size=12),
        )
        self.texto_progresso.grid(row=4, column=0, padx=28, pady=(0, 10), sticky="w")

        painel = ctk.CTkFrame(
            self,
            fg_color=CARD,
            corner_radius=14,
            border_width=1,
            border_color="#E4E7EC",
        )
        painel.grid(row=5, column=0, padx=28, pady=(8, 28), sticky="nsew")
        painel.grid_rowconfigure(1, weight=1)
        painel.grid_columnconfigure(0, weight=1)

        cabecalho = ctk.CTkLabel(
            painel,
            text="Atividade do processamento",
            text_color=TEXTO,
            font=ctk.CTkFont(size=15, weight="bold"),
        )
        cabecalho.grid(row=0, column=0, padx=18, pady=(16, 8), sticky="w")

        self.log = ctk.CTkTextbox(
            painel,
            wrap="word",
            font=("Consolas", 12),
            fg_color="#F8FAFC",
            text_color=TEXTO,
        )
        self.log.grid(row=1, column=0, padx=18, pady=(0, 18), sticky="nsew")
        self.log.configure(state="disabled")

        self.after(100, self._consumir_fila)

    def iniciar(self):
        if self.processando:
            return

        self.processando = True
        self.botao.configure(state="disabled", text="PROCESSANDO...")
        self.status.configure(text="Processando pedidos")
        self.indicador.configure(text_color=AMARELO)
        self.progresso.start()
        self.texto_progresso.configure(text="Buscando e processando solicitações...")

        threading.Thread(
            target=self._executar,
            daemon=True,
        ).start()

    def _executar(self):
        stdout_original = sys.stdout
        stderr_original = sys.stderr
        capturador = SaidaInterface(self.fila)

        try:
            sys.stdout = capturador
            sys.stderr = capturador

            processar_pedidos(
                confirmar_impressao=self._confirmar_impressao,
                confirmar_continuacao=self._confirmar_continuacao,
            )

        except Exception as erro:
            self.fila.put(f"\nERRO INESPERADO: {erro}\n")
            self.after(
                0,
                lambda: messagebox.showerror(
                    "Erro",
                    f"Ocorreu um erro inesperado:\n\n{erro}",
                ),
            )

        finally:
            sys.stdout = stdout_original
            sys.stderr = stderr_original
            self.after(0, self._finalizar)

    def _confirmar_impressao(self, crachas: list[Path]) -> bool:
        resposta = {"valor": False}
        evento = threading.Event()

        nomes = "\n".join(
            f"• {arquivo.stem.split('_', 2)[-1].replace('_', ' ').title()}"
            for arquivo in crachas[:12]
        )
        complemento = "\n..." if len(crachas) > 12 else ""

        def perguntar():
            resposta["valor"] = messagebox.askyesno(
                "Confirmar impressão",
                (
                    f"{len(crachas)} crachá(s) estão prontos.\n\n"
                    f"{nomes}{complemento}\n\n"
                    "Deseja enviar o lote para impressão?"
                ),
            )
            evento.set()

        self.after(0, perguntar)
        evento.wait()
        return resposta["valor"]

    def _confirmar_continuacao(self, arquivo: Path, erro: Exception) -> bool:
        resposta = {"valor": False}
        evento = threading.Event()

        def perguntar():
            resposta["valor"] = messagebox.askyesno(
                "Erro de impressão",
                (
                    f"Não foi possível imprimir:\n{arquivo.name}\n\n"
                    f"{erro}\n\nDeseja continuar com o próximo?"
                ),
            )
            evento.set()

        self.after(0, perguntar)
        evento.wait()
        return resposta["valor"]

    def _finalizar(self):
        self.processando = False
        self.progresso.stop()
        self.progresso.set(1)
        self.botao.configure(state="normal", text="INICIAR PROCESSAMENTO")
        self.status.configure(text="Processamento finalizado")
        self.indicador.configure(text_color=SUCESSO)
        self.texto_progresso.configure(text="Execução concluída")

    def _consumir_fila(self):
        alterou = False

        while True:
            try:
                texto = self.fila.get_nowait()
            except queue.Empty:
                break

            self.log.configure(state="normal")
            self.log.insert("end", texto)
            self.log.configure(state="disabled")
            alterou = True

        if alterou:
            self.log.see("end")

        self.after(100, self._consumir_fila)
