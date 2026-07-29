from pathlib import Path
import time

import win32con
import win32print
import win32ui
from PIL import Image, ImageWin


NOME_IMPRESSORA_PADRAO = "IDP CUBO1 Card Printer"

TEMPO_LIMITE_FILA = 180
INTERVALO_CONSULTA_FILA = 1
PAUSA_APOS_FILA_ESVAZIAR = 3


class ErroImpressao(Exception):
    """Erro relacionado ao envio ou acompanhamento da impressão."""


def listar_impressoras() -> list[str]:
    flags = (
        win32print.PRINTER_ENUM_LOCAL
        | win32print.PRINTER_ENUM_CONNECTIONS
    )

    return [
        impressora[2]
        for impressora in win32print.EnumPrinters(flags)
    ]


def verificar_impressora(
    nome_impressora: str = NOME_IMPRESSORA_PADRAO,
) -> None:
    impressoras = listar_impressoras()

    if nome_impressora not in impressoras:
        raise ErroImpressao(
            f'Impressora não encontrada: "{nome_impressora}"'
        )


def obter_trabalhos_fila(
    nome_impressora: str = NOME_IMPRESSORA_PADRAO,
) -> list:
    """
    Retorna os trabalhos atualmente registrados na fila
    da impressora.
    """

    handle = None

    try:
        handle = win32print.OpenPrinter(nome_impressora)

        informacoes = win32print.GetPrinter(
            handle,
            2,
        )

        quantidade = informacoes.get("cJobs", 0)

        if quantidade <= 0:
            return []

        return win32print.EnumJobs(
            handle,
            0,
            quantidade,
            1,
        )

    finally:
        if handle is not None:
            win32print.ClosePrinter(handle)


def fila_esta_vazia(
    nome_impressora: str = NOME_IMPRESSORA_PADRAO,
) -> bool:
    return len(
        obter_trabalhos_fila(nome_impressora)
    ) == 0


def aguardar_fila_esvaziar(
    nome_impressora: str = NOME_IMPRESSORA_PADRAO,
    tempo_limite: int = TEMPO_LIMITE_FILA,
    pausa_final: int = PAUSA_APOS_FILA_ESVAZIAR,
) -> None:
    """
    Aguarda até não haver mais trabalhos no spooler.

    A pausa final reduz o risco de enviar o próximo cartão
    enquanto a impressora ainda está finalizando mecanicamente
    o cartão anterior.
    """

    inicio = time.monotonic()
    aviso_exibido = False

    while not fila_esta_vazia(nome_impressora):

        if not aviso_exibido:
            print("Aguardando a fila da impressora esvaziar...")
            aviso_exibido = True

        tempo_decorrido = time.monotonic() - inicio

        if tempo_decorrido >= tempo_limite:
            raise ErroImpressao(
                "A fila da impressora não esvaziou dentro "
                f"do limite de {tempo_limite} segundos."
            )

        time.sleep(INTERVALO_CONSULTA_FILA)

    if aviso_exibido:
        print("Fila da impressora esvaziada.")

    if pausa_final > 0:
        print(
            f"Aguardando {pausa_final} segundos "
            "para finalização mecânica..."
        )
        time.sleep(pausa_final)


def imprimir_cracha(
    caminho_imagem: str | Path,
    nome_impressora: str = NOME_IMPRESSORA_PADRAO,
    aguardar_antes: bool = True,
    aguardar_depois: bool = True,
) -> None:
    caminho_imagem = Path(caminho_imagem)

    if not caminho_imagem.exists():
        raise FileNotFoundError(
            f"Crachá não encontrado: {caminho_imagem}"
        )

    verificar_impressora(nome_impressora)

    if aguardar_antes:
        aguardar_fila_esvaziar(
            nome_impressora=nome_impressora,
            pausa_final=0,
        )

    imagem = Image.open(caminho_imagem).convert("RGB")

    # A arte do crachá é vertical, mas o driver da Cubo1
    # trabalha com a área física do cartão em paisagem.
    if imagem.height > imagem.width:
        imagem = imagem.rotate(
            90,
            expand=True,
        )

    dc = win32ui.CreateDC()

    try:
        dc.CreatePrinterDC(nome_impressora)

        largura_imprimivel = dc.GetDeviceCaps(
            win32con.HORZRES
        )

        altura_imprimivel = dc.GetDeviceCaps(
            win32con.VERTRES
        )

        largura_imagem, altura_imagem = imagem.size

        escala = min(
            largura_imprimivel / largura_imagem,
            altura_imprimivel / altura_imagem,
        )

        largura_final = int(
            largura_imagem * escala
        )

        altura_final = int(
            altura_imagem * escala
        )

        x = int(
            (largura_imprimivel - largura_final) / 2
        )

        y = int(
            (altura_imprimivel - altura_final) / 2
        )

        nome_documento = (
            f"Crachá - {caminho_imagem.stem}"
        )

        print()
        print(f"Enviando para impressão: {caminho_imagem.name}")
        print(f"Impressora: {nome_impressora}")
        print(
            f"Área imprimível: "
            f"{largura_imprimivel} x {altura_imprimivel}"
        )
        print(
            f"Imagem enviada: "
            f"{largura_final} x {altura_final}"
        )

        dc.StartDoc(nome_documento)
        dc.StartPage()

        dib = ImageWin.Dib(imagem)

        dib.draw(
            dc.GetHandleOutput(),
            (
                x,
                y,
                x + largura_final,
                y + altura_final,
            ),
        )

        dc.EndPage()
        dc.EndDoc()

        print("Crachá enviado para a fila de impressão.")

    except Exception as erro:
        try:
            dc.AbortDoc()
        except Exception:
            pass

        raise ErroImpressao(
            f"Falha ao imprimir {caminho_imagem.name}: {erro}"
        ) from erro

    finally:
        dc.DeleteDC()
        imagem.close()

    if aguardar_depois:
        aguardar_fila_esvaziar(
            nome_impressora=nome_impressora,
        )

    print(f"Impressão finalizada: {caminho_imagem.name}")