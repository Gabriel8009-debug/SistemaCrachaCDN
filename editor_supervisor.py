from __future__ import annotations

import tkinter as tk
from pathlib import Path

from app.ui.supervisor_template_editor import SupervisorTemplateEditor


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    editor = SupervisorTemplateEditor(
        master=root,
        project_dir=Path(__file__).resolve().parent,
    )
    editor.protocol("WM_DELETE_WINDOW", root.destroy)
    root.mainloop()
