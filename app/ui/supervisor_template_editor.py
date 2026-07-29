from __future__ import annotations

import json
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageTk


class SupervisorTemplateEditor(tk.Toplevel):
    ELEMENTOS = (
        "foto",
        "nome",
        "cargo",
        "documento",
        "linha_esquerda",
        "linha_direita",
    )

    def __init__(
        self,
        master=None,
        project_dir: str | Path | None = None,
    ) -> None:
        super().__init__(master)

        self.project_dir = (
            Path(project_dir)
            if project_dir
            else Path(__file__).resolve().parents[2]
        )
        self.config_path = (
            self.project_dir / "config" / "supervisor_layout.json"
        )

        self.title("Editor visual — Crachá de Supervisor")
        self.geometry("1040x760")
        self.minsize(980, 720)

        self.layout = json.loads(
            self.config_path.read_text(encoding="utf-8")
        )

        self.template = self._load_template()
        self.preview_photo = self._load_default_photo()

        self.scale = min(0.68, 650 / self.template.height)
        self.selected = "foto"
        self.drag_origin: tuple[int, int] | None = None
        self.tk_images: dict[str, ImageTk.PhotoImage] = {}

        self._build_ui()
        self._bind_events()
        self.redraw()

    def _resolve(self, value: str) -> Path:
        path = Path(value)
        return path if path.is_absolute() else self.project_dir / path

    def _load_template(self) -> Image.Image:
        return Image.open(
            self._resolve(self.layout["template"])
        ).convert("RGBA")

    def _load_default_photo(self) -> Image.Image:
        reference = self.project_dir / "templates" / "referencia_supervisor.png"
        if reference.exists():
            image = Image.open(reference).convert("RGBA")
            return image.crop((155, 286, 482, 652))
        return Image.new("RGBA", (320, 360), "#D9D9D9")

    def _build_ui(self) -> None:
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(
            self,
            background="#2B2B2B",
            highlightthickness=0,
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")

        panel = tk.Frame(self, width=300, padx=14, pady=14)
        panel.grid(row=0, column=1, sticky="ns")
        panel.grid_propagate(False)

        tk.Label(
            panel,
            text="EDITOR DO SUPERVISOR",
            font=("Arial", 14, "bold"),
        ).pack(anchor="w", pady=(0, 12))

        tk.Label(
            panel,
            text=(
                "Clique no elemento e arraste.\n"
                "Roda do mouse: redimensiona.\n"
                "Setas: ajuste fino.\n"
                "Shift + setas: 10 px.\n"
                "Ctrl + S: salvar."
            ),
            justify="left",
        ).pack(anchor="w")

        self.selection_label = tk.Label(
            panel,
            text="",
            font=("Arial", 11, "bold"),
        )
        self.selection_label.pack(anchor="w", pady=(18, 5))

        self.values_label = tk.Label(panel, text="", justify="left")
        self.values_label.pack(anchor="w")

        tk.Button(
            panel,
            text="Carregar template limpo",
            command=self.choose_template,
            width=28,
        ).pack(pady=(24, 5))

        tk.Button(
            panel,
            text="Carregar foto de teste",
            command=self.choose_photo,
            width=28,
        ).pack(pady=5)

        tk.Button(
            panel,
            text="Salvar configuração",
            command=self.save,
            width=28,
        ).pack(pady=5)

        tk.Button(
            panel,
            text="Gerar prévia PNG",
            command=self.export_preview,
            width=28,
        ).pack(pady=5)

        tk.Button(
            panel,
            text="Fechar",
            command=self.destroy,
            width=28,
        ).pack(pady=(5, 0))

    def _bind_events(self) -> None:
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<MouseWheel>", self.on_wheel)

        self.bind("<Control-s>", lambda _e: self.save())
        self.bind("<Control-S>", lambda _e: self.save())
        self.bind("<Left>", lambda e: self.nudge(-self._step(e), 0))
        self.bind("<Right>", lambda e: self.nudge(self._step(e), 0))
        self.bind("<Up>", lambda e: self.nudge(0, -self._step(e)))
        self.bind("<Down>", lambda e: self.nudge(0, self._step(e)))

    @staticmethod
    def _step(event) -> int:
        return 10 if event.state & 0x0001 else 1

    def choose_template(self) -> None:
        path = filedialog.askopenfilename(
            title="Selecione o template limpo",
            filetypes=[("Imagem PNG", "*.png"), ("Imagens", "*.png;*.jpg;*.jpeg")],
        )
        if not path:
            return

        self.layout["template"] = str(Path(path))
        self.template = Image.open(path).convert("RGBA")
        self.scale = min(0.68, 650 / self.template.height)
        self.redraw()

    def choose_photo(self) -> None:
        path = filedialog.askopenfilename(
            title="Selecione uma foto de teste",
            filetypes=[("Imagens", "*.png;*.jpg;*.jpeg;*.webp")],
        )
        if not path:
            return

        self.preview_photo = Image.open(path).convert("RGBA")
        self.redraw()

    def _scaled(self, value: float) -> int:
        return round(value * self.scale)

    def _unscaled(self, value: float) -> int:
        return round(value / self.scale)

    def _element_rects(self) -> dict[str, tuple[int, int, int, int]]:
        l = self.layout
        photo = l["foto"]
        name = l["nome"]
        cargo = l["cargo"]
        doc = l["documento"]

        return {
            "foto": (
                photo["x"],
                photo["y"],
                photo["x"] + photo.get("diametro", photo["largura"]),
                photo["y"] + photo.get("diametro", photo["altura"]),
            ),
            "nome": (
                name["x_centro"] - name["largura_maxima"] // 2,
                name["y"],
                name["x_centro"] + name["largura_maxima"] // 2,
                name["y"] + name["tamanho"] + 18,
            ),
            "cargo": (
                cargo["x_centro"] - 180,
                cargo["y"],
                cargo["x_centro"] + 180,
                cargo["y"] + cargo["tamanho"] + 14,
            ),
            "documento": (
                doc["x_centro"] - 240,
                doc["y"],
                doc["x_centro"] + 240,
                doc["y"] + doc["tamanho"] + 14,
            ),
            "linha_esquerda": self._line_rect(l["linha_esquerda"]),
            "linha_direita": self._line_rect(l["linha_direita"]),
        }

    @staticmethod
    def _line_rect(line: dict) -> tuple[int, int, int, int]:
        return (
            min(line["x1"], line["x2"]) - 8,
            min(line["y1"], line["y2"]) - 8,
            max(line["x1"], line["x2"]) + 8,
            max(line["y1"], line["y2"]) + 8,
        )

    def on_click(self, event) -> None:
        x = self._unscaled(event.x)
        y = self._unscaled(event.y)

        for element, rect in reversed(list(self._element_rects().items())):
            if rect[0] <= x <= rect[2] and rect[1] <= y <= rect[3]:
                self.selected = element
                self.drag_origin = (x, y)
                self.redraw()
                return

    def on_drag(self, event) -> None:
        if not self.drag_origin:
            return

        x = self._unscaled(event.x)
        y = self._unscaled(event.y)
        dx = x - self.drag_origin[0]
        dy = y - self.drag_origin[1]
        self._move_selected(dx, dy)
        self.drag_origin = (x, y)
        self.redraw()

    def on_release(self, _event) -> None:
        self.drag_origin = None

    def nudge(self, dx: int, dy: int) -> None:
        self._move_selected(dx, dy)
        self.redraw()

    def _move_selected(self, dx: int, dy: int) -> None:
        item = self.layout[self.selected]

        if self.selected == "foto":
            item["x"] += dx
            item["y"] += dy
        elif self.selected in ("nome", "cargo", "documento"):
            item["x_centro"] += dx
            item["y"] += dy
        else:
            item["x1"] += dx
            item["x2"] += dx
            item["y1"] += dy
            item["y2"] += dy

    def on_wheel(self, event) -> None:
        direction = 1 if event.delta > 0 else -1
        item = self.layout[self.selected]

        if self.selected == "foto":
            diametro = max(
                80,
                int(item.get("diametro", item.get("largura", 300)))
                + direction * 4,
            )
            item["diametro"] = diametro
            item["largura"] = diametro
            item["altura"] = diametro
        elif self.selected in ("nome", "cargo", "documento"):
            item["tamanho"] = max(10, item["tamanho"] + direction)
        else:
            item["x2"] += direction * 4

        self.redraw()

    def _font(
        self,
        size: int,
        element: str = "texto",
        bold: bool = False,
    ):
        font_key = {
            "nome": "fonte_nome",
            "cargo": "fonte_cargo",
            "documento": "fonte_documento",
        }.get(element)

        if font_key:
            value = self.layout.get(font_key)
            if value:
                path = self._resolve(value)
                if path.exists():
                    return ImageFont.truetype(str(path), size)

        if bold:
            value = self.layout.get("fonte_nome")
            if value:
                path = self._resolve(value)
                if path.exists():
                    return ImageFont.truetype(str(path), size)

        try:
            return ImageFont.truetype("arial.ttf", size)
        except OSError:
            return ImageFont.load_default()

    def _render(self, selection: bool = True) -> Image.Image:
        image = self.template.copy()
        draw = ImageDraw.Draw(image)
        l = self.layout

        photo = l["foto"]
        diametro = int(
            photo.get(
                "diametro",
                min(photo.get("largura", 300), photo.get("altura", 300)),
            )
        )
        photo["largura"] = diametro
        photo["altura"] = diametro

        fitted = ImageOps.fit(
            self.preview_photo,
            (diametro, diametro),
            Image.Resampling.LANCZOS,
            centering=(
                photo.get("centragem_x", 0.5),
                photo.get("centragem_y", 0.42),
            ),
        )
        if photo.get("circular", True):
            mask = Image.new("L", (diametro, diametro), 0)
            ImageDraw.Draw(mask).ellipse(
                (0, 0, diametro - 1, diametro - 1),
                fill=255,
            )
            fitted.putalpha(mask)
        image.alpha_composite(fitted, dest=(photo["x"], photo["y"]))

        self._draw_center(
            draw,
            "Luciana Adão",
            l["nome"],
            self._font(l["nome"]["tamanho"], element="nome", bold=True),
        )
        self._draw_center(
            draw,
            l["cargo"]["texto"],
            l["cargo"],
            self._font(l["cargo"]["tamanho"], element="cargo"),
        )
        self._draw_center(
            draw,
            "RG: 010.900.048-9",
            l["documento"],
            self._font(l["documento"]["tamanho"], element="documento"),
        )

        for key in ("linha_esquerda", "linha_direita"):
            line = l[key]
            draw.line(
                (line["x1"], line["y1"], line["x2"], line["y2"]),
                fill=line["cor"],
                width=line["espessura"],
            )

        if selection:
            rect = self._element_rects()[self.selected]
            draw.rectangle(rect, outline="#FF0000", width=2)

        return image

    @staticmethod
    def _draw_center(draw, text, cfg, font) -> None:
        bbox = draw.textbbox((0, 0), text, font=font)
        width = bbox[2] - bbox[0]
        draw.text(
            (cfg["x_centro"] - width / 2, cfg["y"]),
            text,
            font=font,
            fill=cfg["cor"],
        )

    def redraw(self) -> None:
        image = self._render(selection=True)
        display = image.resize(
            (
                self._scaled(image.width),
                self._scaled(image.height),
            ),
            Image.Resampling.LANCZOS,
        )

        tk_image = ImageTk.PhotoImage(display)
        self.tk_images["preview"] = tk_image
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, image=tk_image, anchor="nw")
        self.canvas.configure(
            scrollregion=(0, 0, display.width, display.height)
        )

        self.selection_label.configure(
            text=f"Selecionado: {self.selected}"
        )
        self.values_label.configure(
            text=json.dumps(
                self.layout[self.selected],
                ensure_ascii=False,
                indent=2,
            )
        )

    def save(self) -> None:
        self.config_path.write_text(
            json.dumps(self.layout, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        messagebox.showinfo(
            "Configuração salva",
            f"Layout salvo em:\n{self.config_path}",
        )

    def export_preview(self) -> None:
        path = filedialog.asksaveasfilename(
            title="Salvar prévia",
            defaultextension=".png",
            filetypes=[("Imagem PNG", "*.png")],
        )
        if not path:
            return
        self._render(selection=False).save(path)
        messagebox.showinfo("Prévia gerada", f"Arquivo salvo em:\n{path}")
