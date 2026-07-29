from pathlib import Path

from app.supervisor_badge_generator import gerar_cracha_supervisor


BASE = Path(__file__).resolve().parent

gerar_cracha_supervisor(
    layout_path=BASE / "config" / "supervisor_layout.json",
    foto_path=BASE / "templates" / "referencia_supervisor.png",
    saida_path=BASE / "exemplos" / "cracha_supervisor_teste.png",
    nome="Luciana Adão",
    rg="010.900.048-9",
)

print("Prévia criada em exemplos/cracha_supervisor_teste.png")
