import io
import re
from pathlib import Path

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from app.path_manager import CREDENTIALS, FOTOS_TEMP


CREDENTIALS_PATH = CREDENTIALS / "credenciais.json"
PASTA_FOTOS_TEMP = FOTOS_TEMP


def criar_servico_drive():
    credenciais = Credentials.from_service_account_file(
        CREDENTIALS_PATH,
        scopes=[
            "https://www.googleapis.com/auth/drive.readonly",
        ],
    )

    return build(
        "drive",
        "v3",
        credentials=credenciais,
    )


def extrair_id_drive(link: str) -> str:
    """
    Extrai o ID de diferentes formatos de links do Google Drive.
    """

    link = link.strip()

    padroes = [
        r"[?&]id=([a-zA-Z0-9_-]+)",
        r"/file/d/([a-zA-Z0-9_-]+)",
        r"/d/([a-zA-Z0-9_-]+)",
    ]

    for padrao in padroes:
        resultado = re.search(padrao, link)

        if resultado:
            return resultado.group(1)

    raise ValueError(
        f"Não foi possível encontrar o ID no link: {link}"
    )


def baixar_foto_drive(
    link: str,
    nome_arquivo: str,
) -> Path:
    """
    Baixa uma foto do Google Drive e retorna o caminho salvo.
    """

    PASTA_FOTOS_TEMP.mkdir(
        parents=True,
        exist_ok=True,
    )

    arquivo_id = extrair_id_drive(link)

    servico = criar_servico_drive()

    metadados = (
        servico.files()
        .get(
            fileId=arquivo_id,
            fields="name,mimeType",
        )
        .execute()
    )

    mime_type = metadados.get("mimeType", "")

    extensoes = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
    }

    extensao = extensoes.get(mime_type, ".jpg")

    caminho_saida = (
        PASTA_FOTOS_TEMP
        / f"{nome_arquivo}{extensao}"
    )

    requisicao = (
        servico.files()
        .get_media(fileId=arquivo_id)
    )

    with caminho_saida.open("wb") as arquivo:
        downloader = MediaIoBaseDownload(
            arquivo,
            requisicao,
        )

        concluido = False

        while not concluido:
            _, concluido = downloader.next_chunk()

    return caminho_saida