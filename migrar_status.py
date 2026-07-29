from app.sheets_service import (
    ABA,
    PLANILHA_ID,
    criar_servico_sheets,
)


def obter_valor(celula: dict) -> str:
    return str(celula.get("formattedValue", "")).strip()


def obter_cor_rgb(celula: dict) -> tuple[float, float, float] | None:
    """
    Retorna a cor de fundo efetiva da célula no formato RGB,
    com valores entre 0 e 1.
    """

    formato = celula.get("effectiveFormat", {})

    estilo_cor = formato.get("backgroundColorStyle", {})
    cor = estilo_cor.get("rgbColor")

    # Compatibilidade com respostas que usam backgroundColor.
    if cor is None:
        cor = formato.get("backgroundColor")

    if cor is None:
        return None

    return (
        float(cor.get("red", 0)),
        float(cor.get("green", 0)),
        float(cor.get("blue", 0)),
    )


def rgb_para_hex(cor: tuple[float, float, float] | None) -> str:
    if cor is None:
        return "SEM COR"

    r, g, b = cor

    return "#{:02X}{:02X}{:02X}".format(
        round(r * 255),
        round(g * 255),
        round(b * 255),
    )


def cor_verde_neon(cor: tuple[float, float, float] | None) -> bool:
    if cor is None:
        return False

    r, g, b = cor

    return (
        g >= 0.85
        and r <= 0.30
        and b <= 0.30
    )


def cor_laranja(cor: tuple[float, float, float] | None) -> bool:
    if cor is None:
        return False

    r, g, b = cor

    return (
        r >= 0.85
        and 0.30 <= g <= 0.80
        and b <= 0.30
    )


def migrar_status() -> None:
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
        print("Nenhuma aba encontrada.")
        return

    blocos = abas[0].get("data", [])

    if not blocos:
        print("A aba não possui dados.")
        return

    linhas = blocos[0].get("rowData", [])

    if len(linhas) < 2:
        print("Não existem respostas para migrar.")
        return

    alteracoes = []
    verdes = 0
    laranjas = 0
    pendentes = 0
    ja_preenchidos = 0
    cores_desconhecidas = []

    # Ignora o cabeçalho e começa na linha real 2.
    for numero_linha, linha in enumerate(linhas[1:], start=2):
        celulas = linha.get("values", [])

        # Completa até a coluna I.
        celulas += [{}] * (9 - len(celulas))

        nome = obter_valor(celulas[2])
        status_atual = obter_valor(celulas[8])

        # Ignora linhas sem nome.
        if not nome:
            continue

        # Não altera status que já tenha conteúdo.
        if status_atual:
            ja_preenchidos += 1
            continue

        cor_coluna_c = obter_cor_rgb(celulas[2])

        if cor_verde_neon(cor_coluna_c):
            novo_status = "CRACHÁ PRONTO"
            verdes += 1

        elif cor_laranja(cor_coluna_c):
            novo_status = "PRODUZINDO CRACHÁ"
            laranjas += 1

        else:
            # Branco, cinza-claro ou sem cor continuam pendentes.
            novo_status = ""
            pendentes += 1

            # Registra somente cores que não parecem branca/cinza.
            if cor_coluna_c is not None:
                r, g, b = cor_coluna_c
                brilho_minimo = min(r, g, b)

                if brilho_minimo < 0.85:
                    cores_desconhecidas.append(
                        (
                            numero_linha,
                            nome,
                            rgb_para_hex(cor_coluna_c),
                        )
                    )

        if novo_status:
            alteracoes.append(
                {
                    "range": f"'{ABA}'!I{numero_linha}",
                    "values": [[novo_status]],
                }
            )

    if alteracoes:
        corpo = {
            "valueInputOption": "RAW",
            "data": alteracoes,
        }

        (
            servico.spreadsheets()
            .values()
            .batchUpdate(
                spreadsheetId=PLANILHA_ID,
                body=corpo,
            )
            .execute()
        )

    print()
    print("=" * 60)
    print("MIGRAÇÃO CONCLUÍDA")
    print("=" * 60)
    print(f"Verdes marcados como CRACHÁ PRONTO: {verdes}")
    print(f"Laranjas marcados como PRODUZINDO CRACHÁ: {laranjas}")
    print(f"Brancos/cinzas mantidos pendentes: {pendentes}")
    print(f"Status que já estavam preenchidos: {ja_preenchidos}")
    print(f"Total de células alteradas: {len(alteracoes)}")

    if cores_desconhecidas:
        print()
        print("ATENÇÃO: cores não reconhecidas:")
        print("-" * 60)

        for linha, nome, cor_hex in cores_desconhecidas:
            print(
                f"Linha {linha} | {nome} | Cor {cor_hex}"
            )

    print("=" * 60)


if __name__ == "__main__":
    migrar_status()