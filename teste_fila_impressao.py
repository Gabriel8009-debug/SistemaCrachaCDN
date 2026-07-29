from pathlib import Path

from app.printer_service import (
    ErroImpressao,
    imprimir_cracha,
)


BASE_DIR = Path(__file__).resolve().parent

CRACHAS = [
    BASE_DIR
    / "output"
    / "2026-07-24"
    / "cracha_361_michelle_morabito.png",

    BASE_DIR
    / "output"
    / "2026-07-24"
    / "cracha_348_kayque_xavier.png",
]


def executar_teste() -> None:

    arquivos_existentes = [
        caminho
        for caminho in CRACHAS
        if caminho.exists()
    ]

    if not arquivos_existentes:
        print("Nenhum crachá de teste foi encontrado.")
        return

    print()
    print("=" * 50)
    print("TESTE CONTROLADO DA FILA DE IMPRESSÃO")
    print("=" * 50)

    for indice, caminho in enumerate(
        arquivos_existentes,
        start=1,
    ):
        print(f"{indice}. {caminho.name}")

    print()

    resposta = input(
        f"Enviar {len(arquivos_existentes)} "
        "crachá(s) para impressão? [S/N]: "
    ).strip().lower()

    if resposta != "s":
        print("Teste cancelado.")
        return

    impressos = 0
    erros = 0

    for caminho in arquivos_existentes:

        try:
            imprimir_cracha(caminho)
            impressos += 1

        except (ErroImpressao, FileNotFoundError) as erro:
            erros += 1
            print(f"ERRO: {erro}")

            resposta = input(
                "Deseja continuar com o próximo? [S/N]: "
            ).strip().lower()

            if resposta != "s":
                break

    print()
    print("=" * 50)
    print("RESUMO")
    print("=" * 50)
    print(f"Impressos: {impressos}")
    print(f"Erros: {erros}")


if __name__ == "__main__":
    executar_teste()