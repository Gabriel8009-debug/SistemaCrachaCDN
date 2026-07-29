import logging
import re
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Callable

from app import config
from app.badge_generator import gerar_cracha_corretor
from app.sisweb_service import consultar_sisweb
from app.supervisor_badge_generator import gerar_cracha_supervisor
from app.drive_service import baixar_foto_drive
from app.foto_circular import criar_foto_circular
from app.printer_service import (
    ErroImpressao,
    imprimir_cracha,
)
from app.path_manager import LOGS, OUTPUT, TEMPLATES
from app.sheets_service import (
    atualizar_status,
    listar_pedidos_para_cracha,
)


BASE_DIR = OUTPUT.parent
PASTA_OUTPUT = OUTPUT
PASTA_LOGS = LOGS


def configurar_logger() -> logging.Logger:
    """
    Cria um arquivo de log por dia.
    """

    PASTA_LOGS.mkdir(
        parents=True,
        exist_ok=True,
    )

    data_atual = datetime.now().strftime("%Y-%m-%d")

    caminho_log = (
        PASTA_LOGS
        / f"{data_atual}.log"
    )

    logger = logging.getLogger("sistema_cracha")
    logger.setLevel(logging.INFO)

    # Evita adicionar o mesmo gravador várias vezes.
    if not logger.handlers:
        gravador = logging.FileHandler(
            caminho_log,
            encoding="utf-8",
        )

        formato = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s",
            datefmt="%d/%m/%Y %H:%M:%S",
        )

        gravador.setFormatter(formato)
        logger.addHandler(gravador)

    return logger


def formatar_nome_cracha(nome_completo: str) -> str:
    """
    Mantém o primeiro nome e o último sobrenome relevante.

    Exemplo:
    Núbia dos Santos Nicolau -> Núbia Nicolau
    """

    conectivos = {
        "de",
        "da",
        "do",
        "das",
        "dos",
        "e",
    }

    partes = nome_completo.strip().split()

    if not partes:
        return ""

    if len(partes) <= 2:
        return " ".join(partes)

    primeiro_nome = partes[0]

    sobrenomes_validos = [
        parte
        for parte in partes[1:]
        if parte.lower() not in conectivos
    ]

    if not sobrenomes_validos:
        return primeiro_nome

    ultimo_sobrenome = sobrenomes_validos[-1]

    return f"{primeiro_nome} {ultimo_sobrenome}"


def limpar_nome_arquivo(texto: str) -> str:
    """
    Converte um nome em um formato seguro para arquivo.

    Exemplo:
    Núbia Nicolau -> nubia_nicolau
    """

    texto = unicodedata.normalize(
        "NFKD",
        texto,
    )

    texto = (
        texto
        .encode("ascii", "ignore")
        .decode("ascii")
        .lower()
        .strip()
    )

    texto = re.sub(
        r"[^a-z0-9]+",
        "_",
        texto,
    )

    return texto.strip("_")



def normalizar_texto_comparacao(texto: str) -> str:
    """
    Normaliza um texto para comparação segura.

    Remove acentos, espaços excedentes e diferenças entre
    letras maiúsculas e minúsculas.
    """

    texto = unicodedata.normalize(
        "NFKD",
        str(texto or ""),
    )

    texto = (
        texto
        .encode("ascii", "ignore")
        .decode("ascii")
        .casefold()
    )

    texto = re.sub(
        r"\s+",
        " ",
        texto,
    )

    return texto.strip()


def identificar_supervisor(
    pedido: dict,
) -> tuple[bool, str, str]:
    """
    Identifica o tipo de crachá pelos cabeçalhos reais da planilha.

    Regras:
    - coluna B: Código SISWeb;
    - coluna C: Nome e sobrenome de preferência;
    - coluna E: Nome do Supervisor;
    - quando os nomes das colunas C e E coincidem após normalização,
      o pedido é de supervisor.
    """

    nome_solicitante = str(
        pedido.get(
            "Nome e sobrenome de preferência",
            "",
        )
        or ""
    ).strip()

    nome_supervisor = str(
        pedido.get(
            "Nome do Supervisor",
            "",
        )
        or ""
    ).strip()

    codigo_sisweb = str(
        pedido.get(
            "Código SISWeb",
            "",
        )
        or ""
    ).strip()

    eh_supervisor = bool(
        normalizar_texto_comparacao(nome_solicitante)
        and normalizar_texto_comparacao(nome_supervisor)
        and normalizar_texto_comparacao(nome_solicitante)
        == normalizar_texto_comparacao(nome_supervisor)
    )

    return eh_supervisor, nome_supervisor, codigo_sisweb


def normalizar_telefone(telefone: str) -> str:
    """
    Remove espaços, parênteses e traços.

    Se houver DDD e telefone, adiciona o código 55.
    """

    numeros = re.sub(
        r"\D",
        "",
        telefone,
    )

    if not numeros:
        raise ValueError(
            "O número de WhatsApp está vazio."
        )

    if len(numeros) in {10, 11}:
        numeros = "55" + numeros

    return numeros


def criar_pasta_output_do_dia() -> Path:
    """
    Cria uma pasta no formato output/AAAA-MM-DD.
    """

    data_atual = datetime.now().strftime(
        "%Y-%m-%d"
    )

    pasta_do_dia = (
        PASTA_OUTPUT
        / data_atual
    )

    pasta_do_dia.mkdir(
        parents=True,
        exist_ok=True,
    )

    return pasta_do_dia


def localizar_cracha_existente(
    numero_linha: int,
    tipo_cracha: str,
) -> Path | None:
    """
    Procura apenas um crachá do mesmo tipo para a linha informada.

    Isso impede que um crachá antigo de corretor seja reutilizado
    depois que a linha passa a ser identificada como supervisor.
    """

    if not PASTA_OUTPUT.exists():
        return None

    padrao = (
        f"cracha_{numero_linha}_{tipo_cracha}_*.png"
    )

    arquivos = sorted(
        PASTA_OUTPUT.rglob(padrao),
        key=lambda caminho: caminho.stat().st_mtime,
        reverse=True,
    )

    return arquivos[0] if arquivos else None


def processar_um_pedido(
    pedido: dict,
    pasta_do_dia: Path,
    logger: logging.Logger,
) -> tuple[str, Path | None]:
    """
    Processa uma única solicitação.

    Retorno:
    - ("concluido", caminho_do_cracha)
    - ("ja_existia", None)
    - ("erro", None)
    """

    numero_linha = pedido["_numero_linha"]

    nome_completo = pedido[
        "Nome e sobrenome de preferência"
    ].strip()

    telefone_original = pedido[
        "Número de Whatsapp"
    ].strip()

    link_foto = pedido[
        "Foto (boa qualidade, rosto visível)"
    ].strip()

    (
        eh_supervisor,
        nome_supervisor_planilha,
        codigo_sisweb,
    ) = identificar_supervisor(
        pedido
    )

    nome_cracha = formatar_nome_cracha(
        nome_completo
    )

    telefone = (
        ""
        if eh_supervisor
        else normalizar_telefone(telefone_original)
    )

    nome_arquivo = limpar_nome_arquivo(
        nome_cracha
    )

    print()
    print("=" * 60)
    print(f"Processando linha {numero_linha}")
    print(f"Nome completo: {nome_completo}")
    print(f"Nome no crachá: {nome_cracha}")
    print(
        "Tipo de crachá: "
        + (
            "SUPERVISOR"
            if eh_supervisor
            else "CORRETOR"
        )
    )

    if eh_supervisor:
        print(
            f"Supervisor identificado: "
            f"{nome_supervisor_planilha}"
        )
        print(
            f"Código SisWeb: "
            f"{codigo_sisweb or '[vazio]'}"
        )

    print("=" * 60)

    tipo_cracha = (
        "supervisor"
        if eh_supervisor
        else "corretor"
    )

    logger.info(
        (
            "Linha %s iniciada | nome=%s | tipo=%s | "
            "supervisor_planilha=%s | codigo_sisweb=%s"
        ),
        numero_linha,
        nome_completo,
        tipo_cracha.upper(),
        nome_supervisor_planilha,
        codigo_sisweb,
    )

    cracha_existente = localizar_cracha_existente(
        numero_linha,
        tipo_cracha,
    )

    if cracha_existente is not None:
        print(
            "Crachá já encontrado. "
            "A solicitação não será gerada novamente."
        )
        print(f"Arquivo: {cracha_existente}")

        atualizar_status(
            numero_linha,
            "CRACHÁ PRONTO",
        )

        logger.warning(
            "Linha %s não foi regenerada; "
            "arquivo já existente: %s",
            numero_linha,
            cracha_existente,
        )

        return (
            "ja_existia",
            cracha_existente,
        )

    try:
        atualizar_status(
            numero_linha,
            "PRODUZINDO CRACHÁ",
        )

        logger.info(
            "Linha %s marcada como PRODUZINDO CRACHÁ",
            numero_linha,
        )

        print("Baixando a foto...")

        caminho_foto = baixar_foto_drive(
            link=link_foto,
            nome_arquivo=f"foto_linha_{numero_linha}",
        )

        logger.info(
            "Linha %s | foto baixada: %s",
            numero_linha,
            caminho_foto,
        )

        caminho_cracha = (
            pasta_do_dia
            / (
                f"cracha_{numero_linha}_"
                f"{tipo_cracha}_"
                f"{nome_arquivo}.png"
            )
        )

        if eh_supervisor:
            if not codigo_sisweb:
                raise ValueError(
                    "O pedido foi identificado como supervisor, "
                    "mas o código SisWeb da coluna B está vazio."
                )

            print(
                "Consultando RG/CPF no SisWeb..."
            )

            logger.info(
                "Linha %s | supervisor identificado | "
                "código SisWeb=%s",
                numero_linha,
                codigo_sisweb,
            )

            dados_sisweb = consultar_sisweb(
                codigo_sisweb,
                fechar_ao_final=True,
                abrir_modulo_corretores=True,
            )

            rg = str(
                dados_sisweb.get("rg", "")
                or ""
            ).strip()

            cpf = str(
                dados_sisweb.get("cpf", "")
                or ""
            ).strip()

            nome_sisweb = str(
                dados_sisweb.get("nome", "")
                or ""
            ).strip()

            avisos_sisweb = dados_sisweb.get(
                "avisos",
                [],
            )

            if nome_sisweb:
                logger.info(
                    "Linha %s | SisWeb retornou cadastro: %s",
                    numero_linha,
                    nome_sisweb,
                )

            if avisos_sisweb:
                logger.warning(
                    "Linha %s | avisos do SisWeb: %s",
                    numero_linha,
                    avisos_sisweb,
                )

            if not rg and not cpf:
                raise ValueError(
                    "O SisWeb não retornou RG nem CPF "
                    f"para o código {codigo_sisweb}."
                )

            print(
                "Gerando o crachá de supervisor..."
            )

            gerar_cracha_supervisor(
                foto_path=str(
                    caminho_foto
                ),
                saida_path=str(
                    caminho_cracha
                ),
                nome=nome_cracha,
                rg=rg,
                cpf=cpf,
                cargo="Líder de Vendas",
            )

            logger.info(
                "Linha %s | crachá de supervisor gerado",
                numero_linha,
            )

        else:
            caminho_foto_circular = (
                pasta_do_dia
                / f"foto_circular_{numero_linha}.png"
            )

            print(
                "Criando a foto circular..."
            )

            criar_foto_circular(
                caminho_foto=str(
                    caminho_foto
                ),
                caminho_saida=str(
                    caminho_foto_circular
                ),
                diametro=config.DIAMETRO_FOTO,
            )

            logger.info(
                "Linha %s | foto circular criada",
                numero_linha,
            )

            print(
                "Gerando o crachá de corretor..."
            )

            gerar_cracha_corretor(
                template_path=str(
                    TEMPLATES / "corretor.png"
                ),
                foto_path=str(
                    caminho_foto_circular
                ),
                saida_path=str(
                    caminho_cracha
                ),
                nome=nome_cracha,
                telefone=telefone,
                mensagem_whatsapp=(
                    "Olá, tudo bem?"
                ),
            )

            logger.info(
                "Linha %s | crachá de corretor gerado",
                numero_linha,
            )

        atualizar_status(
            numero_linha,
            "CRACHÁ PRONTO",
        )

        logger.info(
            "Linha %s concluída | crachá: %s",
            numero_linha,
            caminho_cracha,
        )

        print("Pedido concluído.")
        print(f"Crachá salvo em: {caminho_cracha}")

        return (
            "concluido",
            caminho_cracha,
        )

    except Exception as erro:
        print()
        print(
            f"Erro ao processar a linha "
            f"{numero_linha}:"
        )
        print(erro)

        logger.exception(
            "Erro na linha %s | %s",
            numero_linha,
            nome_completo,
        )

        try:
            atualizar_status(
                numero_linha,
                "ERRO NO CRACHÁ",
            )

        except Exception as erro_status:
            logger.exception(
                "Não foi possível atualizar "
                "o status da linha %s: %s",
                numero_linha,
                erro_status,
            )

        return (
            "erro",
            None,
        )


def imprimir_lote(
    crachas_para_imprimir: list[Path],
    logger: logging.Logger,
    confirmar_impressao: Callable[[list[Path]], bool] | None = None,
    confirmar_continuacao: Callable[[Path, Exception], bool] | None = None,
) -> tuple[int, int]:
    """
    Exibe o lote, solicita confirmação e imprime um crachá
    por vez, aguardando a fila da impressora esvaziar.

    Retorna:
    - quantidade de impressos
    - quantidade de erros de impressão
    """

    if not crachas_para_imprimir:
        return 0, 0

    print()
    print("=" * 60)
    print("LOTE DE IMPRESSÃO")
    print("=" * 60)

    for indice, caminho_cracha in enumerate(
        crachas_para_imprimir,
        start=1,
    ):
        partes = caminho_cracha.stem.split("_")
        nome_partes = partes[3:] if len(partes) >= 4 else partes[2:]
        nome_exibicao = (
            " ".join(nome_partes)
            .replace("_", " ")
            .title()
        )

        print(
            f"{indice}. {nome_exibicao}"
        )

    print("-" * 60)
    print(
        f"Total: {len(crachas_para_imprimir)} "
        "crachá(s)"
    )
    print("=" * 60)

    if confirmar_impressao is not None:
        deve_imprimir = confirmar_impressao(
            crachas_para_imprimir
        )
    else:
        resposta = input(
            "Deseja imprimir este lote agora? [S/N]: "
        ).strip().lower()
        deve_imprimir = resposta == "s"

    if not deve_imprimir:
        print()
        print(
            "Impressão cancelada. "
            "Os crachás permanecem salvos na pasta de saída."
        )

        logger.info(
            "Impressão cancelada pelo usuário | lote=%s",
            len(crachas_para_imprimir),
        )

        return 0, 0

    impressos = 0
    erros_impressao = 0

    print()
    print("=" * 60)
    print("INICIANDO IMPRESSÃO")
    print("=" * 60)

    for indice, caminho_cracha in enumerate(
        crachas_para_imprimir,
        start=1,
    ):
        print()
        print(
            f"Imprimindo {indice} de "
            f"{len(crachas_para_imprimir)}"
        )

        try:
            imprimir_cracha(
                caminho_cracha
            )

            impressos += 1

            try:
                partes_nome = caminho_cracha.stem.split("_")

                if len(partes_nome) < 2:
                    raise ValueError(
                        "Não foi possível identificar o número "
                        "da linha no nome do arquivo."
                    )

                numero_linha = int(partes_nome[1])

                atualizar_status(
                    numero_linha,
                    "IMPRESSO",
                )

                print(
                    f"STATUS da linha {numero_linha} "
                    "atualizado para IMPRESSO."
                )

                logger.info(
                    "Status atualizado para IMPRESSO | "
                    "linha=%s | arquivo=%s",
                    numero_linha,
                    caminho_cracha,
                )

            except Exception as erro_status:
                print()
                print(
                    "O crachá foi impresso, mas não foi possível "
                    "atualizar o STATUS para IMPRESSO."
                )
                print(f"Erro: {erro_status}")

                logger.exception(
                    "Crachá impresso, mas houve erro ao atualizar "
                    "o STATUS para IMPRESSO | arquivo=%s",
                    caminho_cracha,
                )

            logger.info(
                "Crachá impresso | arquivo=%s",
                caminho_cracha,
            )

        except (
            ErroImpressao,
            FileNotFoundError,
        ) as erro:
            erros_impressao += 1

            print()
            print(
                f"Erro ao imprimir "
                f"{caminho_cracha.name}:"
            )
            print(erro)

            logger.exception(
                "Erro de impressão | arquivo=%s",
                caminho_cracha,
            )

            if confirmar_continuacao is not None:
                deve_continuar = confirmar_continuacao(
                    caminho_cracha,
                    erro,
                )
            else:
                continuar = input(
                    "Deseja continuar com o próximo? [S/N]: "
                ).strip().lower()
                deve_continuar = continuar == "s"

            if not deve_continuar:
                print(
                    "Impressão interrompida pelo usuário."
                )
                break

    print()
    print("=" * 60)
    print("RESUMO DA IMPRESSÃO")
    print("=" * 60)
    print(f"Crachás impressos: {impressos}")
    print(
        f"Erros de impressão: {erros_impressao}"
    )
    print("=" * 60)

    logger.info(
        (
            "Impressão finalizada | "
            "lote=%s | impressos=%s | erros=%s"
        ),
        len(crachas_para_imprimir),
        impressos,
        erros_impressao,
    )

    return impressos, erros_impressao


def processar_pedidos(
    confirmar_impressao: Callable[[list[Path]], bool] | None = None,
    confirmar_continuacao: Callable[[Path, Exception], bool] | None = None,
) -> None:
    """
    Processa todos os pedidos pendentes encontrados.

    Ao final, apresenta os crachás gerados nesta execução
    e solicita confirmação antes de imprimir o lote.
    """

    inicio = datetime.now()
    logger = configurar_logger()

    print()
    print("Buscando pedidos pendentes...")

    try:
        pedidos = listar_pedidos_para_cracha()

    except Exception:
        logger.exception(
            "Erro ao consultar os pedidos no Google Sheets."
        )
        raise

    total = len(pedidos)

    if total == 0:
        print("Nenhum pedido pendente.")
        logger.info(
            "Execução encerrada sem pedidos pendentes."
        )
        return

    print(
        f"{total} pedido(s) de crachá "
        "pendente(s) encontrado(s)."
    )

    pasta_do_dia = criar_pasta_output_do_dia()

    concluidos = 0
    ja_existiam = 0
    erros = 0

    crachas_para_imprimir: list[Path] = []

    for posicao, pedido in enumerate(
        pedidos,
        start=1,
    ):
        print()
        print(
            f"Pedido {posicao} de {total}"
        )

        resultado, caminho_cracha = processar_um_pedido(
            pedido=pedido,
            pasta_do_dia=pasta_do_dia,
            logger=logger,
        )

        if resultado == "concluido":
            concluidos += 1

            if caminho_cracha is not None:
                crachas_para_imprimir.append(
                    caminho_cracha
                )

        elif resultado == "ja_existia":
            ja_existiam += 1

            if caminho_cracha is not None:
                crachas_para_imprimir.append(
                    caminho_cracha
                )

        elif resultado == "erro":
            erros += 1

    fim_processamento = datetime.now()
    duracao_processamento = (
        fim_processamento - inicio
    )

    print()
    print("=" * 60)
    print("RESUMO DA EXECUÇÃO")
    print("=" * 60)
    print(f"Pedidos encontrados: {total}")
    print(f"Crachás produzidos: {concluidos}")
    print(
        f"Crachás que já existiam: "
        f"{ja_existiam}"
    )
    print(f"Pedidos com erro: {erros}")
    print(
        "Tempo de processamento: "
        f"{str(duracao_processamento).split('.')[0]}"
    )
    print(f"Pasta de saída: {pasta_do_dia}")
    print(f"Arquivo de log: {PASTA_LOGS}")
    print("=" * 60)

    logger.info(
        (
            "Processamento finalizado | encontrados=%s | "
            "produzidos=%s | existentes=%s | erros=%s"
        ),
        total,
        concluidos,
        ja_existiam,
        erros,
    )

    impressos, erros_impressao = imprimir_lote(
        crachas_para_imprimir=crachas_para_imprimir,
        logger=logger,
        confirmar_impressao=confirmar_impressao,
        confirmar_continuacao=confirmar_continuacao,
    )

    fim_total = datetime.now()
    duracao_total = fim_total - inicio

    print()
    print("=" * 60)
    print("EXECUÇÃO FINALIZADA")
    print("=" * 60)
    print(f"Crachás produzidos: {concluidos}")
    print(f"Crachás impressos: {impressos}")
    print(
        f"Erros de geração: {erros}"
    )
    print(
        f"Erros de impressão: {erros_impressao}"
    )
    print(
        "Tempo total: "
        f"{str(duracao_total).split('.')[0]}"
    )
    print("=" * 60)

    logger.info(
        (
            "Execução completa | produzidos=%s | "
            "impressos=%s | erros_geracao=%s | "
            "erros_impressao=%s | duracao=%s"
        ),
        concluidos,
        impressos,
        erros,
        erros_impressao,
        str(duracao_total).split(".")[0],
    )
