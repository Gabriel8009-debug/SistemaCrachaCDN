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
from app.path_manager import OUTPUT
from .theme import (
    AMARELO,
    AMARELO_HOVER,
    AZUL,
    BORDA,
    CARD,
    CARD_SECUNDARIO,
    ERRO,
    FUNDO,
    INFO,
    SUCESSO,
    TEXTO,
    TEXTO_SECUNDARIO,
    TEXTO_SUAVE,
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

        self.output_dir = OUTPUT

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
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(4, weight=1)

        ctk.CTkLabel(
            self,
            text="Produção",
            text_color=TEXTO,
            font=ctk.CTkFont(size=29, weight="bold"),
        ).grid(row=0, column=0, columnspan=2, padx=30, pady=(28, 3), sticky="w")

        ctk.CTkLabel(
            self,
            text="Acompanhe o crachá atual e cada etapa do processamento.",
            text_color=TEXTO_SECUNDARIO,
            font=ctk.CTkFont(size=14),
        ).grid(row=1, column=0, columnspan=2, padx=30, pady=(0, 18), sticky="w")

        topo = ctk.CTkFrame(
            self,
            fg_color=CARD,
            corner_radius=16,
            border_width=1,
            border_color=BORDA,
        )
        topo.grid(row=2, column=0, columnspan=2, padx=30, pady=6, sticky="ew")
        topo.grid_columnconfigure(1, weight=1)

        self.indicador = ctk.CTkLabel(
            topo,
            text="●",
            text_color=SUCESSO,
            font=ctk.CTkFont(size=22),
        )
        self.indicador.grid(row=0, column=0, padx=(20, 10), pady=17)

        bloco_status = ctk.CTkFrame(topo, fg_color="transparent")
        bloco_status.grid(row=0, column=1, pady=12, sticky="w")

        self.status = ctk.CTkLabel(
            bloco_status,
            text="Sistema pronto",
            text_color=TEXTO,
            font=ctk.CTkFont(size=15, weight="bold"),
        )
        self.status.grid(row=0, column=0, sticky="w")

        self.detalhe = ctk.CTkLabel(
            bloco_status,
            text="Nenhuma execução em andamento",
            text_color=TEXTO_SECUNDARIO,
            font=ctk.CTkFont(size=12),
        )
        self.detalhe.grid(row=1, column=0, sticky="w")

        self.botao = ctk.CTkButton(
            topo,
            text="▶  INICIAR PROCESSAMENTO",
            height=46,
            corner_radius=10,
            fg_color=AMARELO,
            hover_color=AMARELO_HOVER,
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
        self.progresso.grid(row=3, column=0, columnspan=2, padx=30, pady=(14, 4), sticky="ew")
        self.progresso.set(0)

        esquerda = ctk.CTkFrame(
            self,
            fg_color=CARD,
            corner_radius=18,
            border_width=1,
            border_color=BORDA,
        )
        esquerda.grid(row=4, column=0, padx=(30, 10), pady=(10, 30), sticky="nsew")
        esquerda.grid_columnconfigure(0, weight=1)
        esquerda.grid_rowconfigure(1, weight=1)

        cabecalho_preview = ctk.CTkFrame(esquerda, fg_color="transparent")
        cabecalho_preview.grid(row=0, column=0, padx=20, pady=(18, 8), sticky="ew")
        cabecalho_preview.grid_columnconfigure(0, weight=1)

        self.texto_progresso = ctk.CTkLabel(
            cabecalho_preview,
            text="Aguardando início",
            text_color=TEXTO_SECUNDARIO,
            font=ctk.CTkFont(size=12),
        )
        self.texto_progresso.grid(row=0, column=0, sticky="w")

        self.nome_atual = ctk.CTkLabel(
            cabecalho_preview,
            text="Nenhum pedido selecionado",
            text_color=TEXTO,
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        self.nome_atual.grid(row=1, column=0, pady=(2, 0), sticky="w")

        self.preview_area = ctk.CTkFrame(
            esquerda,
            fg_color="#E7EBF0",
            corner_radius=16,
        )
        self.preview_area.grid(row=1, column=0, padx=20, pady=(8, 18), sticky="nsew")
        self.preview_area.grid_columnconfigure(0, weight=1)
        self.preview_area.grid_rowconfigure(0, weight=1)

        self.preview = ctk.CTkLabel(
            self.preview_area,
            text="A prévia do crachá\naparecerá aqui",
            text_color=TEXTO_SUAVE,
            font=ctk.CTkFont(size=15, weight="bold"),
        )
        self.preview.grid(row=0, column=0)

        direita = ctk.CTkFrame(self, fg_color="transparent")
        direita.grid(row=4, column=1, padx=(10, 30), pady=(10, 30), sticky="nsew")
        direita.grid_columnconfigure(0, weight=1)
        direita.grid_rowconfigure(1, weight=1)

        resumo = ctk.CTkFrame(
            direita,
            fg_color=AZUL,
            corner_radius=16,
        )
        resumo.grid(row=0, column=0, pady=(0, 10), sticky="ew")
        resumo.grid_columnconfigure((0, 1, 2), weight=1)

        self.valor_pedidos = self._criar_resumo(resumo, 0, "PEDIDOS", "0")
        self.valor_produzidos = self._criar_resumo(resumo, 1, "PRODUZIDOS", "0")
        self.valor_impressos = self._criar_resumo(resumo, 2, "IMPRESSOS", "0")

        timeline = ctk.CTkFrame(
            direita,
            fg_color=CARD,
            corner_radius=18,
            border_width=1,
            border_color=BORDA,
        )
        timeline.grid(row=1, column=0, sticky="nsew")
        timeline.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            timeline,
            text="Etapas do pedido",
            text_color=TEXTO,
            font=ctk.CTkFont(size=17, weight="bold"),
        ).grid(row=0, column=0, columnspan=2, padx=20, pady=(18, 12), sticky="w")

        etapas = [
            ("pedido", "Pedido recebido"),
            ("foto", "Foto baixada e tratada"),
            ("qr", "QR Code gerado"),
            ("cracha", "Crachá montado"),
            ("impressao", "Enviado para impressão"),
        ]

        for indice, (chave, titulo) in enumerate(etapas, start=1):
            marcador = ctk.CTkLabel(
                timeline,
                text="○",
                width=34,
                text_color=TEXTO_SUAVE,
                font=ctk.CTkFont(size=22, weight="bold"),
            )
            marcador.grid(row=indice, column=0, padx=(20, 5), pady=8)

            label = ctk.CTkLabel(
                timeline,
                text=titulo,
                text_color=TEXTO_SECUNDARIO,
                font=ctk.CTkFont(size=13, weight="bold"),
            )
            label.grid(row=indice, column=1, padx=(0, 20), pady=8, sticky="w")
            self.etapas[chave] = (marcador, label)

        self.mensagem = ctk.CTkLabel(
            timeline,
            text="O sistema exibirá aqui a etapa atual.",
            text_color=TEXTO_SECUNDARIO,
            font=ctk.CTkFont(size=12),
            wraplength=340,
            justify="left",
        )
        self.mensagem.grid(
            row=7,
            column=0,
            columnspan=2,
            padx=20,
            pady=(16, 8),
            sticky="w",
        )

        self.tempo = ctk.CTkLabel(
            timeline,
            text="00:00",
            text_color=AZUL,
            font=ctk.CTkFont(size=25, weight="bold"),
        )
        self.tempo.grid(row=8, column=0, padx=20, pady=(0, 16), sticky="w")

        self.botao_log = ctk.CTkButton(
            timeline,
            text="Ver detalhes técnicos",
            width=150,
            fg_color="transparent",
            hover_color="#EEF2F6",
            text_color=AZUL,
            command=self.alternar_log,
        )
        self.botao_log.grid(row=8, column=1, padx=20, pady=(0, 16), sticky="e")

        self.log = ctk.CTkTextbox(
            timeline,
            wrap="word",
            font=("Consolas", 11),
            fg_color="#101828",
            text_color="#D0D5DD",
            height=150,
        )
        self.log_visivel = False

        self.after(100, self._consumir_fila)
        self.after(1000, self._atualizar_tempo)

    def _criar_resumo(self, master, coluna, titulo, valor):
        bloco = ctk.CTkFrame(master, fg_color="transparent")
        bloco.grid(row=0, column=coluna, padx=14, pady=16, sticky="ew")
        ctk.CTkLabel(
            bloco,
            text=titulo,
            text_color="#BFD0E1",
            font=ctk.CTkFont(size=10, weight="bold"),
        ).grid(row=0, column=0, sticky="w")
        label = ctk.CTkLabel(
            bloco,
            text=valor,
            text_color="white",
            font=ctk.CTkFont(size=25, weight="bold"),
        )
        label.grid(row=1, column=0, sticky="w")
        return label

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
        self._atualizar_resumo()
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
            for arquivo in crachas[:10]
        )
        complemento = "\n..." if len(crachas) > 10 else ""

        def perguntar():
            resposta["valor"] = messagebox.askyesno(
                "Confirmar impressão",
                f"{len(crachas)} crachá(s) estão prontos.\n\n"
                f"{nomes}{complemento}\n\nDeseja enviar o lote para impressão?",
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
                "Deseja continuar com o próximo?",
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

    def _atualizar_resumo(self):
        self.valor_pedidos.configure(text=str(self.total_pedidos))
        self.valor_produzidos.configure(text=str(self.produzidos))
        self.valor_impressos.configure(text=str(self.impressos))

    def _limpar_preview(self):
        self.preview.configure(
            image=None,
            text="A prévia do crachá\naparecerá aqui",
        )
        self.preview.image = None
        self.nome_atual.configure(text="Nenhum pedido selecionado")

    def _exibir_preview_arquivo(self, arquivo: Path) -> None:
        """Exibe um PNG específico e registra erros no log técnico."""
        try:
            arquivo = Path(arquivo)
            if not arquivo.is_file():
                self.fila.put(f"[prévia] Arquivo não encontrado: {arquivo}\n")
                return

            with Image.open(arquivo) as origem:
                imagem = origem.convert("RGBA").copy()

            proporcao = imagem.height / max(imagem.width, 1)
            largura = 260
            altura = min(int(largura * proporcao), 430)

            preview_img = ctk.CTkImage(
                light_image=imagem,
                dark_image=imagem,
                size=(largura, altura),
            )
            self.preview.configure(image=preview_img, text="")
            self.preview.image = preview_img
        except Exception as erro:
            self.fila.put(f"[prévia] Falha ao abrir {arquivo}: {erro}\n")

    def _buscar_preview(self, caminho_direto: Path | None = None):
        if caminho_direto is not None:
            arquivo = Path(caminho_direto)
            if arquivo.is_file():
                self._exibir_preview_arquivo(arquivo)
                return

        candidatos: list[Path] = []
        if self.nome_corrente and self.output_dir.exists():
            normalizado = re.sub(
                r"[^a-z0-9]+",
                "_",
                self.nome_corrente.lower(),
            ).strip("_")
            candidatos.extend(self.output_dir.rglob(f"*{normalizado}*.png"))

        if not candidatos and self.output_dir.exists():
            candidatos = list(self.output_dir.rglob("cracha_*.png"))

        candidatos = [arquivo for arquivo in candidatos if arquivo.is_file()]
        if not candidatos:
            self.fila.put(f"[prévia] Nenhum crachá encontrado em {self.output_dir}\n")
            return

        arquivo = max(candidatos, key=lambda item: item.stat().st_mtime_ns)
        self._exibir_preview_arquivo(arquivo)

    def _interpretar_linha(self, texto: str):
        linha = texto.strip()
        if not linha:
            return

        total = re.search(r"(\d+) pedido\(s\).*encontrado", linha, re.I)
        if total:
            self.total_pedidos = int(total.group(1))
            self._atualizar_resumo()
            self.mensagem.configure(
                text=f"{self.total_pedidos} pedido(s) foram localizados."
            )
            return

        atual = re.search(r"Pedido (\d+) de (\d+)", linha, re.I)
        if atual:
            self.pedido_atual = int(atual.group(1))
            self.total_pedidos = int(atual.group(2))
            self._atualizar_resumo()

            fracao = self.pedido_atual / max(self.total_pedidos, 1)
            self.progresso.set(min(fracao * 0.78, 0.78))
            self.texto_progresso.configure(
                text=f"Pedido {self.pedido_atual} de {self.total_pedidos}"
            )
            self._resetar_etapas()
            self._marcar_etapa("pedido", "ativa")
            return

        if linha.startswith("Nome no crachá:"):
            self.nome_corrente = linha.split(":", 1)[1].strip()
            self.nome_atual.configure(text=self.nome_corrente)
            self.mensagem.configure(
                text=f"Preparando o crachá de {self.nome_corrente}."
            )
            self._marcar_etapa("pedido", "concluida")
            self._marcar_etapa("foto", "ativa")
            return

        lower = linha.lower()

        if lower.startswith("crachá salvo em:") or lower.startswith("cracha salvo em:"):
            caminho = Path(linha.split(":", 1)[1].strip().strip('"'))
            self.after(50, lambda p=caminho: self._buscar_preview(p))
            return

        if any(chave in lower for chave in (
            "baixando a foto",
            "foto circular",
            "detectando rosto",
        )):
            self._marcar_etapa("pedido", "concluida")
            self._marcar_etapa("foto", "ativa")
            self.mensagem.configure(
                text="Baixando e tratando a foto do corretor."
            )
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
            self.mensagem.configure(text="Montando o crachá.")
            return

        if "crachá já encontrado" in lower or "ja_existia" in lower:
            self.reutilizados += 1
            self._marcar_etapa("foto", "concluida")
            self._marcar_etapa("qr", "concluida")
            self._marcar_etapa("cracha", "concluida")
            self.mensagem.configure(text="Crachá existente reutilizado.")
            self.after(150, self._buscar_preview)
            return

        if "pedido concluído" in lower or "crachá pronto" in lower:
            self.produzidos += 1
            self._atualizar_resumo()
            self._marcar_etapa("foto", "concluida")
            self._marcar_etapa("qr", "concluida")
            self._marcar_etapa("cracha", "concluida")
            self.mensagem.configure(text="Crachá gerado com sucesso.")
            self.after(250, self._buscar_preview)
            return

        if "iniciando impressão" in lower or "imprimindo " in lower:
            self._marcar_etapa("cracha", "concluida")
            self._marcar_etapa("impressao", "ativa")
            self.progresso.set(max(self.progresso.get(), 0.82))
            self.mensagem.configure(text="Enviando para a impressora.")
            return

        if "impresso" in lower:
            self.impressos += 1
            self._atualizar_resumo()
            self._marcar_etapa("impressao", "concluida")
            self.mensagem.configure(text="Impressão confirmada.")
            return

        if "erro" in lower:
            self.indicador.configure(text_color=ERRO)
            self.mensagem.configure(text=linha)
            for chave in self.etapas:
                marcador, _ = self.etapas[chave]
                if marcador.cget("text") == "●":
                    self._marcar_etapa(chave, "erro")

    def alternar_log(self):
        if self.log_visivel:
            self.log.grid_forget()
            self.botao_log.configure(text="Ver detalhes técnicos")
            self.log_visivel = False
        else:
            self.log.grid(
                row=9,
                column=0,
                columnspan=2,
                padx=20,
                pady=(0, 18),
                sticky="ew",
            )
            self.botao_log.configure(text="Ocultar detalhes")
            self.log_visivel = True

    def _finalizar(self):
        self.processando = False
        self.progresso.set(1)
        self.botao.configure(
            state="normal",
            text="▶  INICIAR NOVAMENTE",
        )
        self.status.configure(text="Processamento finalizado")
        self.detalhe.configure(
            text="O sistema está pronto para uma nova execução"
        )
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
