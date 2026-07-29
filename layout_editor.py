from pathlib import Path
import tkinter as tk
from tkinter import messagebox

from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageTk

from app import config
from app.qrcode_service import gerar_qrcode_whatsapp


BASE_DIR = Path(__file__).resolve().parent

TEMPLATE_PATH = BASE_DIR / "templates" / "corretor.png"
FOTO_PATH = BASE_DIR / "fotos" / "pessoa.jpg"
FONTE_PATH = BASE_DIR / "fonts" / "fonnts.com-Omnium_ExtraBold.otf"
CONFIG_PATH = BASE_DIR / "app" / "config.py"

NOME_TESTE = "Mycon Novais"
TELEFONE_TESTE = "5521999999999"
MENSAGEM_TESTE = "Olá, tudo bem?"


class EditorLayout:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Editor de Layout — Crachá CDN")
        self.root.resizable(False, False)

        self.template = Image.open(TEMPLATE_PATH).convert("RGBA")
        self.largura = self.template.width
        self.altura = self.template.height

        self.canvas = tk.Canvas(
            root,
            width=self.largura,
            height=self.altura,
            highlightthickness=0,
        )
        self.canvas.pack(side="left")

        self.painel = tk.Frame(root, padx=15, pady=15)
        self.painel.pack(side="right", fill="y")

        self.posicao_foto = list(config.POSICAO_FOTO)
        self.diametro_foto = config.DIAMETRO_FOTO

        self.posicao_nome_y = config.POSICAO_NOME_Y
        self.tamanho_fonte_nome = config.TAMANHO_FONTE_NOME

        self.posicao_qrcode = list(config.POSICAO_QRCODE)
        self.tamanho_qrcode = config.TAMANHO_QRCODE

        self.elemento_selecionado = None
        self.inicio_arraste = None

        self.imagens_tk = {}

        self.criar_interface()
        self.desenhar_tudo()
        self.configurar_eventos()

    def criar_interface(self) -> None:
        tk.Label(
            self.painel,
            text="EDITOR DE LAYOUT",
            font=("Arial", 14, "bold"),
        ).pack(pady=(0, 15))

        instrucoes = (
            "1. Clique em um elemento.\n"
            "2. Arraste com o mouse.\n"
            "3. Use a roda para redimensionar.\n"
            "4. Pressione S para salvar.\n\n"
            "No nome, o movimento horizontal\n"
            "é centralizado automaticamente."
        )

        tk.Label(
            self.painel,
            text=instrucoes,
            justify="left",
        ).pack(anchor="w")

        self.label_selecao = tk.Label(
            self.painel,
            text="Selecionado: nenhum",
            font=("Arial", 10, "bold"),
        )
        self.label_selecao.pack(anchor="w", pady=(20, 10))

        self.label_valores = tk.Label(
            self.painel,
            text="",
            justify="left",
        )
        self.label_valores.pack(anchor="w")

        tk.Button(
            self.painel,
            text="Salvar configurações",
            command=self.salvar_configuracoes,
            width=24,
        ).pack(pady=(30, 10))

        tk.Button(
            self.painel,
            text="Fechar",
            command=self.root.destroy,
            width=24,
        ).pack()

    def criar_foto_circular(self) -> Image.Image:
        foto = Image.open(FOTO_PATH).convert("RGBA")

        tamanho = (self.diametro_foto, self.diametro_foto)

        foto = ImageOps.fit(
            foto,
            tamanho,
            method=Image.Resampling.LANCZOS,
            centering=(0.5, 0.4),
        )

        mascara = Image.new("L", tamanho, 0)
        desenho = ImageDraw.Draw(mascara)

        desenho.ellipse(
            (
                0,
                0,
                self.diametro_foto - 1,
                self.diametro_foto - 1,
            ),
            fill=255,
        )

        foto.putalpha(mascara)

        return foto

    def criar_imagem_nome(self) -> Image.Image:
        fonte = ImageFont.truetype(
            str(FONTE_PATH),
            self.tamanho_fonte_nome,
        )

        imagem_temporaria = Image.new("RGBA", (1000, 200), (0, 0, 0, 0))
        desenho = ImageDraw.Draw(imagem_temporaria)

        caixa = desenho.textbbox(
            (0, 0),
            NOME_TESTE,
            font=fonte,
        )

        largura = caixa[2] - caixa[0]
        altura = caixa[3] - caixa[1]

        imagem_nome = Image.new(
            "RGBA",
            (largura + 20, altura + 20),
            (0, 0, 0, 0),
        )

        desenho_nome = ImageDraw.Draw(imagem_nome)

        desenho_nome.text(
            (10 - caixa[0], 10 - caixa[1]),
            NOME_TESTE,
            fill="#000000",
            font=fonte,
        )

        return imagem_nome

    def desenhar_tudo(self) -> None:
        self.canvas.delete("all")
        self.imagens_tk.clear()

        template_tk = ImageTk.PhotoImage(self.template)
        self.imagens_tk["template"] = template_tk

        self.canvas.create_image(
            0,
            0,
            image=template_tk,
            anchor="nw",
            tags="template",
        )

        foto = self.criar_foto_circular()
        foto_tk = ImageTk.PhotoImage(foto)
        self.imagens_tk["foto"] = foto_tk

        self.canvas.create_image(
            self.posicao_foto[0],
            self.posicao_foto[1],
            image=foto_tk,
            anchor="nw",
            tags="foto",
        )

        nome = self.criar_imagem_nome()
        nome_tk = ImageTk.PhotoImage(nome)
        self.imagens_tk["nome"] = nome_tk

        x_nome = (self.largura - nome.width) // 2

        self.canvas.create_image(
            x_nome,
            self.posicao_nome_y,
            image=nome_tk,
            anchor="nw",
            tags="nome",
        )

        qrcode = gerar_qrcode_whatsapp(
            telefone=TELEFONE_TESTE,
            mensagem=MENSAGEM_TESTE,
            tamanho=self.tamanho_qrcode,
        )

        qrcode_tk = ImageTk.PhotoImage(qrcode)
        self.imagens_tk["qrcode"] = qrcode_tk

        self.canvas.create_image(
            self.posicao_qrcode[0],
            self.posicao_qrcode[1],
            image=qrcode_tk,
            anchor="nw",
            tags="qrcode",
        )

        self.destacar_selecionado()
        self.atualizar_painel()

    def configurar_eventos(self) -> None:
        self.canvas.tag_bind("foto", "<Button-1>", self.selecionar_foto)
        self.canvas.tag_bind("nome", "<Button-1>", self.selecionar_nome)
        self.canvas.tag_bind("qrcode", "<Button-1>", self.selecionar_qrcode)

        self.canvas.bind("<B1-Motion>", self.arrastar)
        self.canvas.bind("<ButtonRelease-1>", self.finalizar_arraste)

        self.canvas.bind("<MouseWheel>", self.redimensionar)
        self.root.bind("<KeyPress-s>", self.salvar_configuracoes)
        self.root.bind("<KeyPress-S>", self.salvar_configuracoes)

    def selecionar_foto(self, event) -> None:
        self.selecionar("foto", event)

    def selecionar_nome(self, event) -> None:
        self.selecionar("nome", event)

    def selecionar_qrcode(self, event) -> None:
        self.selecionar("qrcode", event)

    def selecionar(self, elemento: str, event) -> None:
        self.elemento_selecionado = elemento
        self.inicio_arraste = (event.x, event.y)
        self.desenhar_tudo()

    def arrastar(self, event) -> None:
        if self.elemento_selecionado is None:
            return

        if self.inicio_arraste is None:
            self.inicio_arraste = (event.x, event.y)
            return

        deslocamento_x = event.x - self.inicio_arraste[0]
        deslocamento_y = event.y - self.inicio_arraste[1]

        if self.elemento_selecionado == "foto":
            self.posicao_foto[0] += deslocamento_x
            self.posicao_foto[1] += deslocamento_y

        elif self.elemento_selecionado == "qrcode":
            self.posicao_qrcode[0] += deslocamento_x
            self.posicao_qrcode[1] += deslocamento_y

        elif self.elemento_selecionado == "nome":
            self.posicao_nome_y += deslocamento_y

        self.inicio_arraste = (event.x, event.y)
        self.desenhar_tudo()

    def finalizar_arraste(self, event) -> None:
        self.inicio_arraste = None

    def redimensionar(self, event) -> None:
        if self.elemento_selecionado is None:
            return

        variacao = 4 if event.delta > 0 else -4

        if self.elemento_selecionado == "foto":
            self.diametro_foto = max(
                100,
                self.diametro_foto + variacao,
            )

        elif self.elemento_selecionado == "qrcode":
            self.tamanho_qrcode = max(
                80,
                self.tamanho_qrcode + variacao,
            )

        elif self.elemento_selecionado == "nome":
            self.tamanho_fonte_nome = max(
                10,
                self.tamanho_fonte_nome + variacao,
            )

        self.desenhar_tudo()

    def destacar_selecionado(self) -> None:
        if self.elemento_selecionado == "foto":
            x, y = self.posicao_foto

            self.canvas.create_rectangle(
                x,
                y,
                x + self.diametro_foto,
                y + self.diametro_foto,
                outline="red",
                width=2,
            )

        elif self.elemento_selecionado == "qrcode":
            x, y = self.posicao_qrcode

            self.canvas.create_rectangle(
                x,
                y,
                x + self.tamanho_qrcode,
                y + self.tamanho_qrcode,
                outline="red",
                width=2,
            )

    def atualizar_painel(self) -> None:
        selecionado = self.elemento_selecionado or "nenhum"

        self.label_selecao.config(
            text=f"Selecionado: {selecionado}"
        )

        valores = (
            f"Foto: {tuple(self.posicao_foto)}\n"
            f"Diâmetro: {self.diametro_foto}\n\n"
            f"Nome Y: {self.posicao_nome_y}\n"
            f"Fonte: {self.tamanho_fonte_nome}\n\n"
            f"QR Code: {tuple(self.posicao_qrcode)}\n"
            f"Tamanho QR: {self.tamanho_qrcode}"
        )

        self.label_valores.config(text=valores)

    def salvar_configuracoes(self, event=None) -> None:
        conteudo = f'''# FOTO
POSICAO_FOTO = ({self.posicao_foto[0]}, {self.posicao_foto[1]})
DIAMETRO_FOTO = {self.diametro_foto}

# NOME
POSICAO_NOME_Y = {self.posicao_nome_y}
TAMANHO_FONTE_NOME = {self.tamanho_fonte_nome}
CAMINHO_FONTE_NOME = "fonts/Omnium_ExtraBold.otf"

# QR CODE
POSICAO_QRCODE = ({self.posicao_qrcode[0]}, {self.posicao_qrcode[1]})
TAMANHO_QRCODE = {self.tamanho_qrcode}
'''

        CONFIG_PATH.write_text(
            conteudo,
            encoding="utf-8",
        )

        messagebox.showinfo(
            "Configurações salvas",
            "Os valores foram gravados em app/config.py.",
        )


if __name__ == "__main__":
    janela = tk.Tk()
    editor = EditorLayout(janela)
    janela.mainloop()