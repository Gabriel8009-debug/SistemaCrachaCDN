import sys

import win32api
import win32event
import winerror

from app.interface import iniciar_interface


NOME_MUTEX = "SistemaCrachaCDN_InstanciaUnica"


def sistema_ja_esta_aberto() -> bool:
    mutex = win32event.CreateMutex(
        None,
        False,
        NOME_MUTEX,
    )

    if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
        return True

    globals()["_mutex_sistema"] = mutex
    return False


if __name__ == "__main__":
    if sistema_ja_esta_aberto():
        print("O Sistema de Crachás CDN já está em execução.")
        sys.exit(0)

    iniciar_interface()
