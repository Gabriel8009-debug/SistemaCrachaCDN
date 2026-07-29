import queue
import re
import sys
import threading
import time
from pathlib import Path
from tkinter import messagebox

import customtkinter as ctk
from PIL import Image

from app.processador_pedidos import processar_pedidos
from .cards import CardContador
from .theme import (
    AMARELO, AMARELO_HOVER, AZUL, BORDA, CARD, CARD_SECUNDARIO,
    ERRO, FUNDO, INFO, SUCESSO, TEXTO, TEXTO_SECUNDARIO, TEXTO_SUAVE
)


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

        self.base_dir = Path(__file__).resolve().parents[2]
        self.output_dir = self.base_dir / "output"
        self.fotos_dir = self.base_dir / "fotos_temp"

        self.processando = False
        self.fila: queue.Queue[str] = queue.Queue()
        self.inicio_execucao = None

        self.total_pedidos = 0
        self.pedido_atual = 0
        self.produzidos = 0
        self.reutilizados = 0
        self.impressos = 0
        self.nome_corrente = ""
        self.etapas = {}

        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(4, weight=1)

        titulo = ctk.CTkLabel(
            self, text="Produção em tempo real", text_color=TEXTO,
            font=ctk.CTkFont(size=29, weight="bold")
        )
        titulo.grid(row=0, column=0, columnspan=2, padx=30, pady=(28, 3), sticky="w")

        subtitulo = ctk.CTkLabel(
            self,
            text="Acompanhe cada pedido, da leitura da planilha até a impressão.",
            text_color=TEXTO_SECUNDARIO,
            font=ctk.CTkFont(size=14),
        )
        subtitulo.grid(row=1, column=0, columnspan=2, padx=30, pady=(0, 18), sticky="w")

        topo = ctk.CTkFrame(
            self, fg_color=CARD, corner_radius=16, border_width=1, border_color=BORDA
        )
        topo.grid(row=2, column=0, columnspan=2, padx=30, pady=6, sticky="ew")
        topo.grid_columnconfigure(1, weight=1)

        self.indicador = ctk.CTkLabel(
            topo, text="●", text_color=SUCESSO, font=ctk.CTkFont(size=23)
        )
        self.indicador.grid(row=0, column=0, padx=(20, 10), pady=18)

        bloco_status = ctk.CTkFrame(topo, fg_color="transparent")
        bloco_status.grid(row=0, column=1, pady=14, sticky="w")

        self.status = ctk.CTkLabel(
            bloco_status, text="Sistema pronto", text_color=TEXTO,
            font=ctk.CTkFont(size=15, weight="bold")
        )
        self.status.grid(row=0, column=0, sticky="w")

        self.detalhe = ctk.CTkLabel(
            bloco_status, text="Nenhuma execução em andamento",
            text_color=TEXTO_SECUNDARIO, font=ctk.CTkFont(size=12)
        )
        self.detalhe.grid(row=1, column=0, sticky="w")

        self.botao = ctk.CTkButton(
            topo, text="▶  INICIAR PROCESSAMENTO", height=46,
            corner_radius=10, fg_color=AMARELO, hover_color=AMARELO_HOVER,
            text_color=AZUL, font=ctk.CTkFont(size=13, weight="bold"),
            command=self.iniciar,
        )
        self.botao.grid(row=0, column=2, padx=18, pady=14)

        self.progresso = ctk.CTkProgressBar(
            self, progress_color=AMARELO, fg_color="#DDE3EA", height=11
        )
        self.progresso.grid(row=3, column=0, columnspan=2, padx=30, pady=(14, 5), sticky="ew")
        self.progresso.set(0)

        centro = ctk.CTkFrame(self, fg_color="transparent")
        centro.grid(row=4, column=0, padx=(30, 9), pady=(8, 30), sticky="nsew")
        centro.grid_columnconfigure(0, weight=1)
        centro.grid_rowconfigure(1, weight=1)

        self.texto_progresso = ctk.CTkLabel(
            centro, text="Aguardando início", text_color=TEXTO_SECUNDARIO,
            font=ctk.CTkFont(size=12)
        )
        self.texto_progresso.grid(row=0, column=0, pady=(0, 8), sticky="w")

        painel_principal = ctk.CTkFrame(
            centro, fg_color=CARD, corner_radius=16, border_width=1, border_color=BORDA
        )
        painel_principal.grid(row=1, column=0, sticky="nsew")
        painel_principal.grid_columnconfigure(1, weight=1)
        painel_principal.grid_rowconfigure(1, weight=1)

        self.preview_frame = ctk.CTkFrame(
            painel_principal, width=220, fg_color=CARD_SECUNDARIO, corner_radius=14
        )
        self.preview_frame.grid(row=0, column=0, rowspan=2, padx=18, pady=18, sticky="ns")
        self.preview_frame.grid_propagate(False)
        self.preview_frame.grid_columnconfigure(0, weight=1)
        self.preview_frame.grid_rowconfigure(1, weight=1)

        preview_titulo = ctk.CTkLabel(
            self.preview_frame, text="CRACHÁ ATUAL", text_color=TEXTO_SECUNDARIO,
            font=ctk.CTkFont(size=11, weight="bold")
        )
        preview_titulo.grid(row=0, column=0, pady=(14, 8))

        self.preview = ctk.CTkLabel(
            self.preview_frame, text="Nenhuma\nprévia disponível",
            width=170, height=280, corner_radius=12, fg_color="#E9EEF4",
            text_color=TEXTO_SUAVE, font=ctk.CTkFont(size=14, weight="bold")
        )
        self.preview.grid(row=1, column=0, padx=18, pady=(0, 14))

        self.nome_atual = ctk.CTkLabel(
            self.preview_frame, text="Aguardando pedido",
            text_color=TEXTO, font=ctk.CTkFont(size=14, weight="bold"),
            wraplength=180
        )
        self.nome_atual.grid(row=2, column=0, padx=12, pady=(0, 4))

        self.numero_pedido = ctk.CTkLabel(
            self.preview_frame, text="", text_color=TEXTO_SECUNDARIO,
            font=ctk.CTkFont(size=11)
        )
        self.numero_pedido.grid(row=3, column=0, padx=12, pady=(0, 14))

        etapas_frame = ctk.CTkFrame(painel_principal, fg_color="transparent")
        etapas_frame.grid(row=0, column=1, padx=(0, 18), pady=(18, 8), sticky="nsew")
        etapas_frame.grid_columnconfigure(0, weight=1)

        titulo_etapas = ctk.CTkLabel(
            etapas_frame, text="Etapas do processamento",
            text_color=TEXTO, font=ctk.CTkFont(size=17, weight="bold")
        )
        titulo_etapas.grid(row=0, column=0, pady=(0, 10), sticky="w")

        for indice, (chave, titulo_etapa) in enumerate([
            ("pedido", "Pedido localizado"),
            ("foto", "Foto baixada e tratada"),
            ("qr", "QR Code gerado"),
            ("cracha", "Crachá montado"),
            ("impressao", "Enviado para impressão"),
        ], start=1):
            linha = ctk.CTkFrame(etapas_frame, fg_color="#F8FAFC", corner_radius=10)
            linha.grid(row=indice, column=0, pady=4, sticky="ew")
            linha.grid_columnconfigure(1, weight=1)

            marcador = ctk.CTkLabel(
                linha, text="○", text_color=TEXTO_SUAVE,
                font=ctk.CTkFont(size=21, weight="bold"), width=34
            )
            marcador.grid(row=0, column=0, padx=(12, 4), pady=10)

            label = ctk.CTkLabel(
                linha, text=titulo_etapa, text_color=TEXTO_SECUNDARIO,
                font=ctk.CTkFont(size=13, weight="bold")
            )
            label.grid(row=0, column=1, padx=(0, 12), pady=10, sticky="w")

            self.etapas[chave] = (marcador, label)

        rodape = ctk.CTkFrame(painel_principal, fg_color="transparent")
        rodape.grid(row=1, column=1, padx=(0, 18), pady=(8, 18), sticky="sew")
        rodape.grid_columnconfigure(0, weight=1)

        self.mensagem = ctk.CTkLabel(
            rodape, text="O sistema exibirá aqui a etapa atual.",
            text_color=TEXTO_SECUNDARIO, font=ctk.CTkFont(size=12),
            wraplength=560, justify="left"
        )
        self.mensagem.grid(row=0, column=0, sticky="w")

        self.botao_log = ctk.CTkButton(
            rodape, text="Ver detalhes técnicos", width=150,
            fg_color="transparent", hover_color="#EEF2F6",
            text_color=AZUL, command=self.alternar_log
        )
        self.botao_log.grid(row=0, column=1)

        self.log = ctk.CTkTextbox(
            painel_principal, wrap="word", font=("Consolas", 11),
            fg_color="#101828", text_color="#D0D5DD", height=150
        )
        self.log_visivel = False

        lateral = ctk.CTkFrame(self, fg_color="transparent")
        lateral.grid(row=4, column=1, padx=(9, 30), pady=(8, 30), sticky="nsew")
        lateral.grid_columnconfigure((0, 1), weight=1)

        lateral_titulo = ctk.CTkLabel(
            lateral, text="Resumo da execução", text_color=TEXTO,
            font=ctk.CTkFont(size=17, weight="bold")
        )
        lateral_titulo.grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky="w")

        self.card_pedidos = CardContador(lateral, "PEDIDOS", "0", AZUL)
        self.card_pedidos.grid(row=1, column=0, padx=(0, 5), pady=5, sticky="ew")

        self.card_produzidos = CardContador(lateral, "PRODUZIDOS", "0", SUCESSO)
        self.card_produzidos.grid(row=1, column=1, padx=(5, 0), pady=5, sticky="ew")

        self.card_reutilizados = CardContador(lateral, "REUTILIZADOS", "0", AMARELO)
        self.card_reutilizados.grid(row=2, column=0, padx=(0, 5), pady=5, sticky="ew")

        self.card_impressos = CardContador(lateral, "IMPRESSOS", "0", INFO)
        self.card_impressos.grid(row=2, column=1, padx=(5, 0), pady=5, sticky="ew")

        tempo_card = ctk.CTkFrame(
            lateral, fg_color=AZUL, corner_radius=15
        )
        tempo_card.grid(row=3, column=0, columnspan=2, pady=(10, 5), sticky="ew")
        tempo_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            tempo_card, text="TEMPO DE EXECUÇÃO", text_color="#C9D7E6",
            font=ctk.CTkFont(size=11, weight="bold")
        ).grid(row=0, column=0, padx=16, pady=(15, 0), sticky="w")

        self.tempo = ctk.CTkLabel(
            tempo_card, text="00:00", text_color="white",
            font=ctk.CTkFont(size=30, weight="bold")
        )
        self.tempo.grid(row=1, column=0, padx=16, pady=(0, 16), sticky="w")

        self.after(100, self._consumir_fila)
        self.after(1000, self._atualizar_tempo)

    def iniciar(self):
        if self.processando:
            return

        self.processando = True
        self.inicio_execucao = time.time()
        self.total_pedidos = 0
        self.pedido_atual = 0
        self.produzidos = 0
        self.reutilizados = 0
        self.impressos = 0
        self.nome_corrente = ""

        self._resetar_etapas()
        self._atualizar_cards()
        self._limpar_preview()

        self.botao.configure(state="disabled", text="PROCESSANDO...")
        self.status.configure(text="Processamento em andamento")
        self.detalhe.configure(text="Consultando pedidos pendentes")
        self.indicador.configure(text_color=AMARELO)
        self.progresso.set(0.02)
        self.texto_progresso.configure(text="Conectando ao Google Sheets...")
        self.mensagem.configure(text="Iniciando a leitura dos pedidos.")

        threading.Thread(target=self._executar, daemon=True).start()

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
            self.after(0, lambda: messagebox.showerror(
                "Erro", f"Ocorreu um erro inesperado:\n\n{erro}"
            ))
        finally:
            sys.stdout = stdout_original
            sys.stderr = stderr_original
            self.after(0, self._finalizar)

    def _confirmar_impressao(self, crachas: list[Path]) -> bool:
        resposta = {"valor": False}
        evento = threading.Event()

        nomes = "\n".join(
            f"• {arquivo.stem.split('_', 2)[-1].replace('_', ' ').title()}"
            for arquivo in crachas[:10]
        )
        complemento = "\n..." if len(crachas) > 10 else ""

        def perguntar():
            resposta["valor"] = messagebox.askyesno(
                "Confirmar impressão",
                f"{len(crachas)} crachá(s) estão prontos.\n\n"
                f"{nomes}{complemento}\n\nDeseja enviar o lote para impressão?"
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
                f"Não foi possível imprimir:\n{arquivo.name}\n\n{erro}\n\n"
                "Deseja continuar com o próximo?"
            )
            evento.set()

        self.after(0, perguntar)
        evento.wait()
        return resposta["valor"]

    def _marcar_etapa(self, chave: str, estado: str):
        marcador, label = self.etapas[chave]
        if estado == "concluida":
            marcador.configure(text="✓", text_color=SUCESSO)
            label.configure(text_color=TEXTO)
        elif estado == "ativa":
            marcador.configure(text="●", text_color=AMARELO)
            label.configure(text_color=TEXTO)
        elif estado == "erro":
            marcador.configure(text="×", text_color=ERRO)
            label.configure(text_color=ERRO)
        else:
            marcador.configure(text="○", text_color=TEXTO_SUAVE)
            label.configure(text_color=TEXTO_SECUNDARIO)

    def _resetar_etapas(self):
        for chave in self.etapas:
            self._marcar_etapa(chave, "pendente")

    def _atualizar_cards(self):
        self.card_pedidos.valor.configure(text=str(self.total_pedidos))
        self.card_produzidos.valor.configure(text=str(self.produzidos))
        self.card_reutilizados.valor.configure(text=str(self.reutilizados))
        self.card_impressos.valor.configure(text=str(self.impressos))

    def _limpar_preview(self):
        self.preview.configure(
            image=None, text="Nenhuma\nprévia disponível",
            fg_color="#E9EEF4", width=170, height=280
        )
        self.preview.image = None
        self.nome_atual.configure(text="Aguardando pedido")
        self.numero_pedido.configure(text="")

    def _buscar_preview(self):
        candidatos = []
        if self.nome_corrente and self.output_dir.exists():
            normalizado = re.sub(r"[^a-z0-9]+", "_", self.nome_corrente.lower()).strip("_")
            candidatos.extend(self.output_dir.rglob(f"*{normalizado}*.png"))

        candidatos = list(candidatos)
        if not candidatos and self.output_dir.exists():
            candidatos = list(self.output_dir.rglob("cracha_*.png"))

        if not candidatos:
            return

        arquivo = max(candidatos, key=lambda p: p.stat().st_mtime)
        try:
            imagem = Image.open(arquivo)
            proporcao = imagem.height / max(imagem.width, 1)
            largura = 170
            altura = min(int(largura * proporcao), 280)
            preview_img = ctk.CTkImage(
                light_image=imagem, dark_image=imagem, size=(largura, altura)
            )
            self.preview.configure(image=preview_img, text="", fg_color="transparent")
            self.preview.image = preview_img
        except Exception:
            pass

    def _interpretar_linha(self, texto: str):
        linha = texto.strip()
        if not linha:
            return

        total = re.search(r"(\d+) pedido\(s\).*encontrado", linha, re.I)
        if total:
            self.total_pedidos = int(total.group(1))
            self._atualizar_cards()
            self.mensagem.configure(
                text=f"{self.total_pedidos} pedido(s) foram localizados para processamento."
            )
            return

        atual = re.search(r"Pedido (\d+) de (\d+)", linha, re.I)
        if atual:
            self.pedido_atual = int(atual.group(1))
            self.total_pedidos = int(atual.group(2))
            self._atualizar_cards()
            fracao = self.pedido_atual / max(self.total_pedidos, 1)
            self.progresso.set(min(fracao * 0.78, 0.78))
            self.texto_progresso.configure(
                text=f"Pedido {self.pedido_atual} de {self.total_pedidos}"
            )
            self.numero_pedido.configure(
                text=f"Pedido {self.pedido_atual} de {self.total_pedidos}"
            )
            self._resetar_etapas()
            self._marcar_etapa("pedido", "ativa")
            return

        if linha.startswith("Nome no crachá:"):
            self.nome_corrente = linha.split(":", 1)[1].strip()
            self.nome_atual.configure(text=self.nome_corrente)
            self.mensagem.configure(text=f"Preparando o crachá de {self.nome_corrente}.")
            self._marcar_etapa("pedido", "concluida")
            self._marcar_etapa("foto", "ativa")
            return

        lower = linha.lower()

        if "baixando a foto" in lower or "foto circular" in lower or "detectando rosto" in lower:
            self._marcar_etapa("pedido", "concluida")
            self._marcar_etapa("foto", "ativa")
            self.mensagem.configure(text="Baixando e tratando a foto do corretor.")
            return

        if "qr code" in lower or "qrcode" in lower:
            self._marcar_etapa("foto", "concluida")
            self._marcar_etapa("qr", "ativa")
            self.mensagem.configure(text="Gerando o QR Code do WhatsApp.")
            return

        if "gerando o crachá" in lower or "montando crachá" in lower:
            self._marcar_etapa("foto", "concluida")
            self._marcar_etapa("qr", "concluida")
            self._marcar_etapa("cracha", "ativa")
            self.mensagem.configure(text="Montando o crachá com os dados do pedido.")
            return

        if "crachá já encontrado" in lower or "ja_existia" in lower:
            self.reutilizados += 1
            self._marcar_etapa("foto", "concluida")
            self._marcar_etapa("qr", "concluida")
            self._marcar_etapa("cracha", "concluida")
            self.mensagem.configure(text="Um crachá já existente foi reutilizado.")
            self._atualizar_cards()
            self.after(150, self._buscar_preview)
            return

        if "pedido concluído" in lower or "crachá pronto" in lower:
            self.produzidos += 1
            self._marcar_etapa("foto", "concluida")
            self._marcar_etapa("qr", "concluida")
            self._marcar_etapa("cracha", "concluida")
            self.mensagem.configure(text="Crachá gerado com sucesso.")
            self._atualizar_cards()
            self.after(250, self._buscar_preview)
            return

        if "iniciando impressão" in lower or "imprimindo " in lower:
            self._marcar_etapa("cracha", "concluida")
            self._marcar_etapa("impressao", "ativa")
            self.progresso.set(max(self.progresso.get(), 0.82))
            self.mensagem.configure(text="Enviando o crachá para a impressora.")
            return

        if "impresso" in lower or "status da linha" in lower and "impresso" in lower:
            self.impressos += 1
            self._marcar_etapa("impressao", "concluida")
            self._atualizar_cards()
            self.mensagem.configure(text="Impressão confirmada com sucesso.")
            return

        if "erro" in lower:
            self.indicador.configure(text_color=ERRO)
            self.mensagem.configure(text=linha)
            for chave in self.etapas:
                marcador, _ = self.etapas[chave]
                if marcador.cget("text") == "●":
                    self._marcar_etapa(chave, "erro")
            return

    def alternar_log(self):
        if self.log_visivel:
            self.log.grid_forget()
            self.botao_log.configure(text="Ver detalhes técnicos")
            self.log_visivel = False
        else:
            self.log.grid(
                row=2, column=0, columnspan=2,
                padx=18, pady=(0, 18), sticky="ew"
            )
            self.botao_log.configure(text="Ocultar detalhes")
            self.log_visivel = True

    def _finalizar(self):
        self.processando = False
        self.progresso.set(1)
        self.botao.configure(state="normal", text="▶  INICIAR NOVAMENTE")
        self.status.configure(text="Processamento finalizado")
        self.detalhe.configure(text="O sistema está pronto para uma nova execução")
        self.indicador.configure(text_color=SUCESSO)
        self.texto_progresso.configure(text="Execução concluída")
        self.mensagem.configure(text="O fluxo de produção foi finalizado.")

        for chave in self.etapas:
            marcador, _ = self.etapas[chave]
            if marcador.cget("text") == "●":
                self._marcar_etapa(chave, "concluida")

    def _consumir_fila(self):
        while True:
            try:
                texto = self.fila.get_nowait()
            except queue.Empty:
                break

            self.log.configure(state="normal")
            self.log.insert("end", texto)
            self.log.configure(state="disabled")
            self.log.see("end")

            for linha in texto.splitlines():
                self._interpretar_linha(linha)

        self.after(100, self._consumir_fila)

    def _atualizar_tempo(self):
        if self.processando and self.inicio_execucao:
            segundos = int(time.time() - self.inicio_execucao)
            minutos, segundos = divmod(segundos, 60)
            horas, minutos = divmod(minutos, 60)
            if horas:
                texto = f"{horas:02d}:{minutos:02d}:{segundos:02d}"
            else:
                texto = f"{minutos:02d}:{segundos:02d}"
            self.tempo.configure(text=texto)

        self.after(1000, self._atualizar_tempo)
