from pathlib import Path

from app.path_manager import CREDENTIALS

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build


CREDENTIALS_PATH = CREDENTIALS / "credenciais.json"

PLANILHA_ID = "1Qy5cl1zqOy9CjVq10lHYC4pROOa5gpmqpoMnSto7NDU"
ABA = "Respostas do Formulário 1"


# Cores que o sistema aplicará automaticamente.
COR_PRODUZINDO = {
    "red": 0.98,
    "green": 0.60,
    "blue": 0.00,
}

COR_PRONTO = {
    "red": 0.00,
    "green": 1.00,
    "blue": 0.00,
}

COR_ERRO = {
    "red": 0.92,
    "green": 0.20,
    "blue": 0.16,
}


def criar_servico_sheets():
    credenciais = Credentials.from_service_account_file(
        CREDENTIALS_PATH,
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
        ],
    )

    return build(
        "sheets",
        "v4",
        credentials=credenciais,
    )


def obter_valor_celula(celula: dict) -> str:
    """
    Retorna o valor exibido na célula.
    """

    return str(
        celula.get("formattedValue", "")
    ).strip()


def obter_cor_rgb(
    celula: dict,
) -> tuple[float, float, float] | None:
    """
    Retorna a cor de fundo efetiva da célula.

    Os valores RGB ficam entre 0 e 1.
    """

    formato = celula.get("effectiveFormat", {})

    estilo_cor = formato.get(
        "backgroundColorStyle",
        {},
    )

    cor = estilo_cor.get("rgbColor")

    if cor is None:
        cor = formato.get("backgroundColor")

    if cor is None:
        return None

    return (
        float(cor.get("red", 0)),
        float(cor.get("green", 0)),
        float(cor.get("blue", 0)),
    )


def cor_eh_pendente(
    cor: tuple[float, float, float] | None,
) -> bool:
    """
    Considera pendente:

    - ausência de cor;
    - branco;
    - cinza muito claro das linhas alternadas.
    """

    if cor is None:
        return True

    vermelho, verde, azul = cor

    cor_muito_clara = (
        vermelho >= 0.94
        and verde >= 0.94
        and azul >= 0.94
    )

    diferenca_entre_canais = (
        max(vermelho, verde, azul)
        - min(vermelho, verde, azul)
    )

    # Branco ou cinza-claro possuem canais próximos.
    return (
        cor_muito_clara
        and diferenca_entre_canais <= 0.06
    )


def cor_eh_verde(
    cor: tuple[float, float, float] | None,
) -> bool:
    if cor is None:
        return False

    vermelho, verde, azul = cor

    return (
        verde >= 0.80
        and vermelho <= 0.35
        and azul <= 0.35
    )


def cor_eh_laranja(
    cor: tuple[float, float, float] | None,
) -> bool:
    if cor is None:
        return False

    vermelho, verde, azul = cor

    return (
        vermelho >= 0.80
        and 0.30 <= verde <= 0.80
        and azul <= 0.30
    )


def rgb_para_hex(
    cor: tuple[float, float, float] | None,
) -> str:
    if cor is None:
        return "sem cor"

    vermelho, verde, azul = cor

    return "#{:02X}{:02X}{:02X}".format(
        round(vermelho * 255),
        round(verde * 255),
        round(azul * 255),
    )


def listar_pedidos_para_cracha() -> list[dict]:
    """
    Retorna somente solicitações que atendam às duas regras:

    1. STATUS vazio.
    2. Coluna C branca ou cinza-claro.

    Também filtra os tipos:
    - Arte e crachá
    - Apenas crachá
    """

    servico = criar_servico_sheets()

    resposta = (
        servico.spreadsheets()
        .get(
            spreadsheetId=PLANILHA_ID,
            ranges=[f"'{ABA}'!A:I"],
            includeGridData=True,
        )
        .execute()
    )

    abas = resposta.get("sheets", [])

    if not abas:
        raise RuntimeError(
            "Nenhuma aba foi encontrada na planilha."
        )

    blocos = abas[0].get("data", [])

    if not blocos:
        return []

    linhas = blocos[0].get("rowData", [])

    if len(linhas) < 2:
        return []

    celulas_cabecalho = linhas[0].get(
        "values",
        [],
    )

    celulas_cabecalho += [{}] * (
        9 - len(celulas_cabecalho)
    )

    cabecalho = [
        obter_valor_celula(celula)
        for celula in celulas_cabecalho[:9]
    ]

    pedidos = []
    inconsistencias = []

    for numero_linha, linha in enumerate(
        linhas[1:],
        start=2,
    ):
        celulas = linha.get("values", [])

        celulas += [{}] * (9 - len(celulas))

        valores = [
            obter_valor_celula(celula)
            for celula in celulas[:9]
        ]

        nome = valores[2].strip()
        tipo_solicitacao = valores[7].lower().strip()
        status = valores[8].upper().strip()

        if not nome:
            continue

        precisa_de_cracha = tipo_solicitacao in {
            "arte e crachá",
            "apenas crachá",
        }

        if not precisa_de_cracha:
            continue

        cor_coluna_c = obter_cor_rgb(
            celulas[2]
        )

        cor_pendente = cor_eh_pendente(
            cor_coluna_c
        )

        status_vazio = status == ""

        # Somente esta combinação pode ser processada.
        if status_vazio and cor_pendente:
            pedido = dict(
                zip(cabecalho, valores)
            )

            pedido["_numero_linha"] = numero_linha

            pedidos.append(pedido)
            continue

        # Situações incoerentes são bloqueadas.
        if status_vazio and cor_eh_verde(cor_coluna_c):
            inconsistencias.append(
                (
                    numero_linha,
                    nome,
                    "cor verde, mas STATUS vazio",
                )
            )

        elif status_vazio and cor_eh_laranja(cor_coluna_c):
            inconsistencias.append(
                (
                    numero_linha,
                    nome,
                    "cor laranja, mas STATUS vazio",
                )
            )

        elif (
            status == "CRACHÁ PRONTO"
            and cor_pendente
        ):
            inconsistencias.append(
                (
                    numero_linha,
                    nome,
                    "STATUS pronto, mas cor branca/cinza",
                )
            )

        elif (
            status == "PRODUZINDO CRACHÁ"
            and not cor_eh_laranja(cor_coluna_c)
        ):
            inconsistencias.append(
                (
                    numero_linha,
                    nome,
                    (
                        "STATUS produzindo, mas a cor não "
                        "está laranja"
                    ),
                )
            )

    if inconsistencias:
        print()
        print("=" * 60)
        print("INCONSISTÊNCIAS ENCONTRADAS")
        print("=" * 60)

        for linha, nome, motivo in inconsistencias:
            print(
                f"Linha {linha} | {nome} | {motivo}"
            )

        print("=" * 60)
        print()

    return pedidos


def obter_id_da_aba(servico) -> int:
    """
    Retorna o ID interno da aba do Google Sheets.
    """

    resposta = (
        servico.spreadsheets()
        .get(
            spreadsheetId=PLANILHA_ID,
            fields="sheets.properties",
        )
        .execute()
    )

    for aba in resposta.get("sheets", []):
        propriedades = aba.get(
            "properties",
            {},
        )

        if propriedades.get("title") == ABA:
            return propriedades["sheetId"]

    raise RuntimeError(
        f'A aba "{ABA}" não foi encontrada.'
    )


def obter_cor_para_status(
    novo_status: str,
) -> dict | None:
    """
    Define qual cor deve ser aplicada na coluna C.
    """

    status = novo_status.upper().strip()

    if status == "PRODUZINDO CRACHÁ":
        return COR_PRODUZINDO

    if status == "CRACHÁ PRONTO":
        return COR_PRONTO

    if status == "ERRO NO CRACHÁ":
        return COR_ERRO

    return None


def atualizar_status(
    numero_linha: int,
    novo_status: str,
) -> None:
    """
    Atualiza simultaneamente:

    - coluna I: texto do STATUS;
    - coluna C: cor correspondente ao STATUS.
    """

    servico = criar_servico_sheets()

    # Primeiro atualiza o texto da coluna I.
    intervalo_status = (
        f"'{ABA}'!I{numero_linha}"
    )

    corpo_status = {
        "values": [[novo_status]],
    }

    (
        servico.spreadsheets()
        .values()
        .update(
            spreadsheetId=PLANILHA_ID,
            range=intervalo_status,
            valueInputOption="RAW",
            body=corpo_status,
        )
        .execute()
    )

    cor = obter_cor_para_status(novo_status)

    if cor is None:
        return

    sheet_id = obter_id_da_aba(servico)

    # Índices da API começam em zero.
    indice_linha = numero_linha - 1

    requisicao_cor = {
        "requests": [
            {
                "repeatCell": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": indice_linha,
                        "endRowIndex": indice_linha + 1,
                        "startColumnIndex": 2,
                        "endColumnIndex": 3,
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "backgroundColor": cor,
                        }
                    },
                    "fields": (
                        "userEnteredFormat."
                        "backgroundColor"
                    ),
                }
            }
        ]
    }

    (
        servico.spreadsheets()
        .batchUpdate(
            spreadsheetId=PLANILHA_ID,
            body=requisicao_cor,
        )
        .execute()
    )

    print(
        f"Linha {numero_linha}: "
        f"STATUS atualizado para {novo_status}."
    )