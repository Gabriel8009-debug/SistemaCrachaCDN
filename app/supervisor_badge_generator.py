from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont, ImageOps

from app.path_manager import CONFIG, RESOURCE_DIR


BASE_DIR = RESOURCE_DIR
LAYOUT_PADRAO = CONFIG / "supervisor_layout.json"

PREPOSICOES = {
    "da",
    "de",
    "do",
    "das",
    "dos",
    "e",
}


def _carregar_layout(caminho_layout: str | Path) -> dict[str, Any]:
    caminho = Path(caminho_layout)

    if not caminho.exists():
        raise FileNotFoundError(
            f"Arquivo de layout do supervisor não encontrado: {caminho}"
        )

    try:
        with caminho.open("r", encoding="utf-8") as arquivo:
            layout = json.load(arquivo)
    except json.JSONDecodeError as erro:
        raise ValueError(
            f"O JSON do layout do supervisor é inválido: {erro}"
        ) from erro

    campos_obrigatorios = {
        "template",
        "foto",
        "nome",
        "cargo",
        "documento",
        "linha_esquerda",
        "linha_direita",
    }

    ausentes = sorted(campos_obrigatorios - set(layout))

    if ausentes:
        raise ValueError(
            "O layout do supervisor não possui os campos obrigatórios: "
            + ", ".join(ausentes)
        )

    return layout


def _resolver_caminho(
    caminho_layout: Path,
    valor: str | None,
) -> Path | None:
    if not valor:
        return None

    caminho = Path(valor)

    if caminho.is_absolute():
        return caminho

    # O JSON fica em config/. Os caminhos relativos partem da raiz do projeto.
    raiz_projeto = caminho_layout.parent.parent
    return raiz_projeto / caminho


def _carregar_fonte(
    caminho: Path | None,
    tamanho: int,
) -> ImageFont.ImageFont:
    if tamanho <= 0:
        raise ValueError("O tamanho da fonte deve ser maior que zero.")

    if caminho is not None and caminho.exists():
        return ImageFont.truetype(str(caminho), tamanho)

    fontes_fallback = (
        "arial.ttf",
        "Arial.ttf",
        "DejaVuSans.ttf",
    )

    for fonte in fontes_fallback:
        try:
            return ImageFont.truetype(fonte, tamanho)
        except OSError:
            continue

    return ImageFont.load_default()


def _padronizar_nome(nome: str) -> str:
    palavras = str(nome or "").strip().lower().split()

    if not palavras:
        raise ValueError("O nome do supervisor está vazio.")

    resultado: list[str] = []

    for indice, palavra in enumerate(palavras):
        if indice > 0 and palavra in PREPOSICOES:
            resultado.append(palavra)
        else:
            resultado.append(palavra.capitalize())

    return " ".join(resultado)


def _ajustar_fonte_para_largura(
    desenho: ImageDraw.ImageDraw,
    texto: str,
    caminho_fonte: Path | None,
    tamanho_inicial: int,
    largura_maxima: int,
    tamanho_minimo: int = 14,
) -> ImageFont.ImageFont:
    tamanho = int(tamanho_inicial)

    while tamanho >= tamanho_minimo:
        fonte = _carregar_fonte(caminho_fonte, tamanho)
        caixa = desenho.textbbox((0, 0), texto, font=fonte)
        largura = caixa[2] - caixa[0]

        if largura <= largura_maxima:
            return fonte

        tamanho -= 1

    return _carregar_fonte(caminho_fonte, tamanho_minimo)


def _criar_foto_circular(
    caminho_foto: str | Path,
    diametro: int,
    centralizacao: tuple[float, float],
) -> Image.Image:
    caminho = Path(caminho_foto)

    if not caminho.exists():
        raise FileNotFoundError(f"Foto não encontrada: {caminho}")

    if diametro <= 0:
        raise ValueError("O diâmetro da foto deve ser maior que zero.")

    with Image.open(caminho) as imagem_original:
        foto = imagem_original.convert("RGBA")

    foto = ImageOps.fit(
        foto,
        (diametro, diametro),
        method=Image.Resampling.LANCZOS,
        centering=centralizacao,
    )

    mascara = Image.new(
        "L",
        (diametro, diametro),
        0,
    )

    desenho_mascara = ImageDraw.Draw(mascara)
    desenho_mascara.ellipse(
        (0, 0, diametro - 1, diametro - 1),
        fill=255,
    )

    foto.putalpha(mascara)
    return foto


def _desenhar_texto_centralizado(
    desenho: ImageDraw.ImageDraw,
    texto: str,
    x_centro: int,
    y: int,
    fonte: ImageFont.ImageFont,
    cor: str,
) -> None:
    caixa = desenho.textbbox(
        (0, 0),
        texto,
        font=fonte,
    )

    largura = caixa[2] - caixa[0]

    # Compensa o deslocamento interno da fonte para centralização real.
    x = float(x_centro) - (largura / 2) - caixa[0]

    desenho.text(
        (x, int(y)),
        texto,
        font=fonte,
        fill=cor,
    )


def _formatar_cpf(cpf: str) -> str:
    digitos = re.sub(r"\D", "", str(cpf or ""))

    if len(digitos) != 11:
        return str(cpf or "").strip()

    return (
        f"{digitos[:3]}."
        f"{digitos[3:6]}."
        f"{digitos[6:9]}-"
        f"{digitos[9:]}"
    )


def escolher_documento(
    rg: str = "",
    cpf: str = "",
) -> tuple[str, str]:
    rg_limpo = str(rg or "").strip()
    cpf_limpo = str(cpf or "").strip()

    if rg_limpo:
        return "RG", rg_limpo

    if cpf_limpo:
        return "CPF", _formatar_cpf(cpf_limpo)

    raise ValueError(
        "Não foi informado RG nem CPF para o crachá do supervisor."
    )


def gerar_cracha_supervisor(
    foto_path: str | Path,
    saida_path: str | Path,
    nome: str,
    rg: str = "",
    cpf: str = "",
    cargo: str = "Líder de Vendas",
    layout_path: str | Path = LAYOUT_PADRAO,
) -> Path:
    """
    Gera o crachá de supervisor usando o layout calibrado no editor.

    Regras:
    - A foto é sempre circular.
    - O nome usa Omnium ExtraBold, conforme o JSON.
    - O cargo usa Roboto Condensed, conforme o JSON.
    - O documento usa RG; quando não existir, usa CPF.
    """

    caminho_layout = Path(layout_path)
    layout = _carregar_layout(caminho_layout)

    template_path = _resolver_caminho(
        caminho_layout,
        layout.get("template"),
    )

    fonte_nome_path = _resolver_caminho(
        caminho_layout,
        layout.get("fonte_nome"),
    )

    fonte_cargo_path = _resolver_caminho(
        caminho_layout,
        layout.get("fonte_cargo"),
    )

    fonte_documento_path = _resolver_caminho(
        caminho_layout,
        layout.get("fonte_documento"),
    )

    if template_path is None or not template_path.exists():
        raise FileNotFoundError(
            f"Template do supervisor não encontrado: {template_path}"
        )

    with Image.open(template_path) as imagem_template:
        cracha = imagem_template.convert("RGBA")

    desenho = ImageDraw.Draw(cracha)

    foto_cfg = layout["foto"]

    diametro = int(
        foto_cfg.get(
            "diametro",
            min(
                int(foto_cfg.get("largura", 0)),
                int(foto_cfg.get("altura", 0)),
            ),
        )
    )

    foto = _criar_foto_circular(
        caminho_foto=foto_path,
        diametro=diametro,
        centralizacao=(
            float(foto_cfg.get("centragem_x", 0.5)),
            float(foto_cfg.get("centragem_y", 0.5)),
        ),
    )

    cracha.alpha_composite(
        foto,
        dest=(
            int(foto_cfg["x"]),
            int(foto_cfg["y"]),
        ),
    )

    nome_cfg = layout["nome"]
    nome_formatado = _padronizar_nome(nome)

    fonte_nome = _ajustar_fonte_para_largura(
        desenho=desenho,
        texto=nome_formatado,
        caminho_fonte=fonte_nome_path,
        tamanho_inicial=int(nome_cfg["tamanho"]),
        largura_maxima=int(nome_cfg["largura_maxima"]),
    )

    _desenhar_texto_centralizado(
        desenho=desenho,
        texto=nome_formatado,
        x_centro=int(nome_cfg["x_centro"]),
        y=int(nome_cfg["y"]),
        fonte=fonte_nome,
        cor=str(nome_cfg["cor"]),
    )

    cargo_cfg = layout["cargo"]
    texto_cargo = str(cargo or cargo_cfg.get("texto", "Líder de Vendas"))

    fonte_cargo = _carregar_fonte(
        fonte_cargo_path,
        int(cargo_cfg["tamanho"]),
    )

    _desenhar_texto_centralizado(
        desenho=desenho,
        texto=texto_cargo,
        x_centro=int(cargo_cfg["x_centro"]),
        y=int(cargo_cfg["y"]),
        fonte=fonte_cargo,
        cor=str(cargo_cfg["cor"]),
    )

    for chave_linha in (
        "linha_esquerda",
        "linha_direita",
    ):
        linha = layout[chave_linha]

        desenho.line(
            (
                int(linha["x1"]),
                int(linha["y1"]),
                int(linha["x2"]),
                int(linha["y2"]),
            ),
            fill=str(linha["cor"]),
            width=int(linha["espessura"]),
        )

    tipo_documento, numero_documento = escolher_documento(
        rg=rg,
        cpf=cpf,
    )

    documento_cfg = layout["documento"]

    if tipo_documento == "RG":
        prefixo = str(documento_cfg.get("prefixo_rg", "RG:"))
    else:
        prefixo = str(documento_cfg.get("prefixo_cpf", "CPF:"))

    texto_documento = f"{prefixo} {numero_documento}".strip()

    fonte_documento = _carregar_fonte(
        fonte_documento_path,
        int(documento_cfg["tamanho"]),
    )

    _desenhar_texto_centralizado(
        desenho=desenho,
        texto=texto_documento,
        x_centro=int(documento_cfg["x_centro"]),
        y=int(documento_cfg["y"]),
        fonte=fonte_documento,
        cor=str(documento_cfg["cor"]),
    )

    caminho_saida = Path(saida_path)
    caminho_saida.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # PNG é salvo em RGB para manter compatibilidade com o fluxo de impressão.
    cracha.convert("RGB").save(
        caminho_saida,
        format="PNG",
        optimize=True,
    )

    return caminho_saida
