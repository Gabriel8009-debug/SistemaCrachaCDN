from __future__ import annotations

import json
import re
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import pyautogui
import pyperclip
from pywinauto import Desktop

from .vision import SisWebVisionReader

BASE_DIR = Path(__file__).resolve().parent.parent
COORDENADAS_PADRAO = BASE_DIR / "config" / "sisweb_coordenadas.json"
REGIOES_PADRAO = BASE_DIR / "config" / "sisweb_regioes.json"
DEBUG_PADRAO = BASE_DIR / "logs" / "sisweb_debug"


class SisWebAutomationError(RuntimeError):
    """Falha controlada durante a automação do SisWeb."""


@dataclass
class SisWebData:
    codigo: str
    nome: str = ""
    cpf: str = ""
    rg: str = ""
    email: str = ""
    telefone: str = ""
    avisos: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class SisWebService:
    def __init__(
        self,
        coordinates_path: str | Path,
        regions_path: str | Path,
        debug_dir: str | Path | None = None,
        window_title_regex: str = r"^SisWeb$",
    ) -> None:
        self.coordinates_path = Path(coordinates_path)
        self.regions_path = Path(regions_path)
        self.window_title_regex = window_title_regex
        self.debug_dir = Path(debug_dir) if debug_dir else None

        if not self.coordinates_path.exists():
            raise FileNotFoundError(
                f"Coordenadas não encontradas: {self.coordinates_path}"
            )
        if not self.regions_path.exists():
            raise FileNotFoundError(
                f"Regiões não encontradas: {self.regions_path}"
            )

        self.coordinates = json.loads(
            self.coordinates_path.read_text(encoding="utf-8")
        )
        self.vision = SisWebVisionReader(
            self.regions_path,
            self.debug_dir,
        )

    def _window(self):
        windows = Desktop(backend="uia").windows(
            title_re=self.window_title_regex
        )
        if not windows:
            raise SisWebAutomationError(
                "A janela principal do SisWeb não foi encontrada."
            )

        window = windows[0]
        window.set_focus()
        time.sleep(0.5)
        return window

    def _point(self, key: str, window) -> tuple[int, int]:
        try:
            item = self.coordinates["pontos"][key]
        except KeyError as exc:
            raise SisWebAutomationError(
                f"Ponto de calibração ausente: {key}"
            ) from exc

        rect = window.rectangle()
        x = round(rect.left + float(item["x_relativo"]) * rect.width())
        y = round(rect.top + float(item["y_relativo"]) * rect.height())
        return x, y

    def _click(
        self,
        key: str,
        window,
        clicks: int = 1,
        wait: float = 0.65,
    ) -> None:
        x, y = self._point(key, window)
        pyautogui.click(
            x=x,
            y=y,
            clicks=clicks,
            interval=0.16,
        )
        time.sleep(wait)

    @staticmethod
    def _clean_text(value: str) -> str:
        value = value or ""
        value = re.sub(r"\s+", " ", value)
        return value.strip()

    @staticmethod
    def _clean_name(value: str) -> str:
        value = SisWebService._clean_text(value)
        # Remove apenas o sufixo visual da equipe, quando existir.
        value = re.sub(
            r"\s*\(EQUIPE\s+[^)]*\)\s*$",
            "",
            value,
            flags=re.IGNORECASE,
        )
        return value.strip()

    @staticmethod
    def _clean_email(value: str) -> str:
        value = SisWebService._clean_text(value)
        match = re.search(
            r"[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}",
            value,
            flags=re.IGNORECASE,
        )
        return match.group(0).lower() if match else value.lower()

    def _copy_control(self, key: str, window) -> str:
        self._click(key, window, wait=0.25)
        pyperclip.copy("")
        pyautogui.hotkey("ctrl", "a")
        time.sleep(0.12)
        pyautogui.hotkey("ctrl", "c")
        time.sleep(0.35)
        return self._clean_text(pyperclip.paste())

    def _open_corretores(self, window) -> bool:
        """
        Tenta abrir Corretores pela árvore UIA.

        A correção importante aqui é usar descendants() no wrapper da janela,
        em vez de chamar child_window() diretamente no UIAWrapper.
        """
        try:
            candidates = window.descendants(
                title="Corretores",
                control_type="Button",
            )
            for candidate in candidates:
                if candidate.is_visible() and candidate.is_enabled():
                    candidate.click_input()
                    time.sleep(1.2)
                    return True
        except Exception:
            pass

        return False

    def _search_and_open(self, code: str, window) -> None:
        self._click("campo_pesquisa", window, wait=0.2)
        pyautogui.hotkey("ctrl", "a")
        pyautogui.write(str(code), interval=0.07)
        pyautogui.press("enter")
        time.sleep(1.8)

        self._click(
            "primeira_linha_resultado",
            window,
            clicks=2,
            wait=1.8,
        )

    def _read_basic_data(
        self,
        window,
    ) -> tuple[str, str, str, list[str]]:
        warnings: list[str] = []

        self._click("aba_dados_basicos", window)

        name = self._clean_name(
            self._copy_control("campo_nome", window)
        )
        email = self._clean_email(
            self._copy_control("campo_email", window)
        )
        cpf, attempts = self.vision.read_cpf()

        if not name:
            warnings.append("O nome não foi copiado do SisWeb.")
        if not email:
            warnings.append("O e-mail não foi copiado do SisWeb.")
        if not cpf:
            warnings.append(
                "O CPF não foi reconhecido pelo OCR. "
                f"Tentativas executadas: {len(attempts)}."
            )

        return name, email, cpf, warnings

    def _read_phone(self, window) -> tuple[str, list[str]]:
        warnings: list[str] = []

        self._click("aba_telefones", window)
        phone, attempts = self.vision.read_phone()

        if not phone:
            warnings.append(
                "O telefone não foi reconhecido pelo OCR. "
                f"Tentativas executadas: {len(attempts)}."
            )

        return phone, warnings

    def _read_rg(self, window) -> tuple[str, list[str]]:
        warnings: list[str] = []

        self._click("aba_documentos", window)
        rg, attempts = self.vision.read_rg()

        if not rg:
            warnings.append(
                "O RG não foi reconhecido pelo OCR. "
                f"Tentativas executadas: {len(attempts)}."
            )

        return rg, warnings

    def close_registration(self) -> None:
        """
        Fecha a ficha atual com ESC.

        Mantido separado para não fechar uma tela incorreta caso o SisWeb
        esteja em estado inesperado.
        """
        pyautogui.press("esc")
        time.sleep(0.8)

    def buscar_por_codigo(
        self,
        codigo: str | int,
        *,
        abrir_modulo_corretores: bool = True,
        fechar_ao_final: bool = False,
    ) -> dict[str, Any]:
        code = re.sub(r"\D", "", str(codigo))

        if not code:
            raise ValueError("O código SisWeb precisa conter números.")

        window = self._window()
        warnings: list[str] = []

        if abrir_modulo_corretores:
            opened = self._open_corretores(window)
            if not opened:
                warnings.append(
                    "O botão Corretores não foi localizado por UI Automation. "
                    "A pesquisa continuará considerando que a tela de "
                    "Corretores já está aberta."
                )

        self._search_and_open(code, window)

        name, email, cpf, basic_warnings = self._read_basic_data(window)
        phone, phone_warnings = self._read_phone(window)
        rg, rg_warnings = self._read_rg(window)

        warnings.extend(basic_warnings)
        warnings.extend(phone_warnings)
        warnings.extend(rg_warnings)

        result = SisWebData(
            codigo=code,
            nome=name,
            cpf=cpf,
            rg=rg,
            email=email,
            telefone=phone,
            avisos=warnings,
        )

        if fechar_ao_final:
            self.close_registration()

        return result.to_dict()


def criar_sisweb_service(
    *,
    debug: bool = False,
    window_title_regex: str = r"^SisWeb$",
) -> SisWebService:
    """
    Cria o serviço usando os arquivos padrão do SistemaCracha.
    """

    debug_dir = DEBUG_PADRAO if debug else None

    return SisWebService(
        coordinates_path=COORDENADAS_PADRAO,
        regions_path=REGIOES_PADRAO,
        debug_dir=debug_dir,
        window_title_regex=window_title_regex,
    )


def consultar_sisweb(
    codigo: str | int,
    *,
    fechar_ao_final: bool = True,
    abrir_modulo_corretores: bool = True,
    debug: bool = False,
) -> dict[str, Any]:
    """
    Consulta um cadastro do SisWeb pelo código.

    Retorna:
        {
            "codigo": "...",
            "nome": "...",
            "cpf": "...",
            "rg": "...",
            "email": "...",
            "telefone": "...",
            "avisos": [...]
        }
    """

    servico = criar_sisweb_service(debug=debug)

    return servico.buscar_por_codigo(
        codigo,
        abrir_modulo_corretores=abrir_modulo_corretores,
        fechar_ao_final=fechar_ao_final,
    )
