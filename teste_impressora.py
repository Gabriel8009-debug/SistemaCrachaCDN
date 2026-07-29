import win32print


NOME_ESPERADO = "IDP CUBO1 Card Printer"


def listar_impressoras():
    flags = (
        win32print.PRINTER_ENUM_LOCAL
        | win32print.PRINTER_ENUM_CONNECTIONS
    )

    impressoras = win32print.EnumPrinters(flags)

    print("\nImpressoras encontradas:\n")

    encontrada = False

    for impressora in impressoras:
        nome = impressora[2]
        print(f"- {nome}")

        if nome.strip().lower() == NOME_ESPERADO.lower():
            encontrada = True

    print()

    if encontrada:
        print("IDP CUBO1 encontrada com sucesso!")
    else:
        print("IDP CUBO1 não foi encontrada.")
        print(
            f'Confira se o nome no Windows é exatamente: '
            f'"{NOME_ESPERADO}"'
        )


if __name__ == "__main__":
    listar_impressoras()