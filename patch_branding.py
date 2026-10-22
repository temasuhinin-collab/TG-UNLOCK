from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent / "upstream"


def read_text(relative: str) -> str:
    path = ROOT / relative
    if not path.is_file():
        raise SystemExit(f"Не найден исходный файл: {relative}")
    return path.read_text(encoding="utf-8")


def write_text(relative: str, content: str) -> None:
    (ROOT / relative).write_text(content, encoding="utf-8", newline="\n")


def replace_exact(relative: str, old: str, new: str) -> None:
    text = read_text(relative)
    count = text.count(old)
    if count != 1:
        raise SystemExit(
            f"Безопасная остановка: в {relative} ожидалось одно совпадение, найдено {count}. "
            "Версия upstream могла измениться; не применяю сомнительный патч."
        )
    write_text(relative, text.replace(old, new, 1))


def patch_settings_header() -> None:
    relative = "ui/settings_form.py"
    source = read_text(relative)
    start = source.find("def _create_header(ctk, frame, theme):")
    end = source.find("\ndef _create_interface(", start)
    if start < 0 or end < 0:
        raise SystemExit("Не удалось найти функцию заголовка настроек; UI не изменён.")

    replacement = '''def _create_header(ctk, frame, theme):
    """TG UNLOCK branded header with direct developer contact; no donation CTA."""
    header = ctk.CTkFrame(frame, fg_color="transparent")
    header.pack(fill="x", pady=(0, 10))

    title_row = ctk.CTkFrame(header, fg_color="transparent")
    title_row.pack(fill="x")
    ctk.CTkLabel(
        title_row, text="TG UNLOCK",
        font=(theme.ui_font_family, 20, "bold"),
        text_color=theme.text_primary, anchor="w",
    ).pack(side="left")
    ctk.CTkLabel(
        title_row, text=f"v{__version__}",
        font=(theme.ui_font_family, 11),
        text_color=theme.text_secondary, anchor="e",
    ).pack(side="right", padx=(6, 0))

    contact_row = ctk.CTkFrame(header, fg_color="transparent")
    contact_row.pack(fill="x", pady=(3, 0))
    ctk.CTkLabel(
        contact_row,
        text="Автор приложения: Artem_Sukhinin",
        font=(theme.ui_font_family, 10),
        text_color=theme.text_secondary,
        anchor="w",
    ).pack(side="left", fill="x", expand=True)
    contact_button = ctk.CTkButton(
        contact_row,
        text="Связаться ↗",
        width=112,
        height=30,
        font=(theme.ui_font_family, 12, "bold"),
        corner_radius=9,
        fg_color=theme.tg_blue,
        hover_color=theme.tg_blue_hover,
        text_color="#ffffff",
        border_width=0,
        command=lambda: webbrowser.open("https://t.me/artem_sukhinin"),
    )
    contact_button.pack(side="right", padx=(8, 0))
    attach_ctk_tooltip(contact_button, "Открыть Telegram и написать разработчику")
    ctk.CTkFrame(
        header, fg_color=theme.field_border, height=1, corner_radius=0,
    ).pack(fill="x", pady=(10, 0))
'''
    write_text(relative, source[:start] + replacement + source[end:])


def main() -> None:
    replace_exact("utils/tray_common.py", 'APP_NAME = "TgWsProxy"', 'APP_NAME = "TG UNLOCK"')
    replace_exact(
        "utils/tray_common.py",
        'PORTABLE_DIR_NAME = "TgWsProxy_data"',
        'PORTABLE_DIR_NAME = "TG_UNLOCK_data"',
    )
