from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent / "upstream"


def replace_once(path: str, old: str, new: str) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(
            f"Expected exactly one occurrence of {old!r} in {path}; found {count}. "
            "Stopping rather than making a risky patch."
        )
    target.write_text(text.replace(old, new, 1), encoding="utf-8")


def main() -> None:
    # App identity and user-data directories.
    replace_once("utils/tray_common.py", 'APP_NAME = "TgWsProxy"', 'APP_NAME = "TG UNLOCK"')
    replace_once(
        "utils/tray_common.py",
        'PORTABLE_DIR_NAME = "TgWsProxy_data"',
        'PORTABLE_DIR_NAME = "TG_UNLOCK_data"',
    )

    # Use a unique mutex so this branded app does not collide with the upstream build.
    win_path = ROOT / "windows.py"
    win_text = win_path.read_text(encoding="utf-8")
    win_text = win_text.replace(
        "Local\\\\TgWsProxy_SingleInstance",
        "Local\\\\TG_UNLOCK_SingleInstance",
    )
    win_path.write_text(win_text, encoding="utf-8")

    # Rename visible app/window titles while retaining the existing translations.
    locale_dir = ROOT / "ui" / "i18n"
    for locale_file in locale_dir.glob("*.json"):
        try:
            data = json.loads(locale_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        is_ru = locale_file.stem.lower().startswith("ru")
        replacements = {
            "app.name": "TG UNLOCK",
            "app.error_title": "TG UNLOCK — Ошибка" if is_ru else "TG UNLOCK — Error",
            "app.settings_title": "TG UNLOCK — Настройки" if is_ru else "TG UNLOCK — Settings",
            "app.update_title": "TG UNLOCK — Обновление" if is_ru else "TG UNLOCK — Update",
        }
        for key, value in replacements.items():
            if key in data:
                data[key] = value
        locale_file.write_text(
            json.dumps(data, ensure_ascii=False, separators=(",", ": ")) + "\n",
            encoding="utf-8",
        )

    # Put the developer credit inside the Settings window, not only in documentation.
    ui_path = ROOT / "ui" / "ctk_tray_ui.py"
    ui = ui_path.read_text(encoding="utf-8")
    anchor = '    attach_ctk_tooltip(cancel_btn, t("tip.cancel"))\n'
    footer = anchor + '''    ctk.CTkLabel(
        frame,
        text="TG UNLOCK  •  разработчик Artem_Sukhinin",
        font=(theme.ui_font_family, 10),
        text_color=theme.text_secondary,
    ).pack(anchor="center", pady=(8, 0))
'''
    if "разработчик Artem_Sukhinin" not in ui:
        if ui.count(anchor) != 1:
            raise SystemExit(
                "Could not find the expected Settings button block; UI patch aborted safely."
            )
        ui_path.write_text(ui.replace(anchor, footer, 1), encoding="utf-8")

    # Give the Windows executable the requested name.
    spec_path = ROOT / "packaging" / "windows.spec"
    spec = spec_path.read_text(encoding="utf-8")
    if "name='TgWsProxy'" in spec:
        spec = spec.replace("name='TgWsProxy'", "name='TG_UNLOCK'", 1)
    elif 'name="TgWsProxy"' in spec:
        spec = spec.replace('name="TgWsProxy"', 'name="TG_UNLOCK"', 1)
    else:
        raise SystemExit("Could not find executable name in packaging/windows.spec.")
    spec_path.write_text(spec, encoding="utf-8")
    print("TG UNLOCK branding and in-app attribution applied successfully.")


if __name__ == "__main__":
    main()
