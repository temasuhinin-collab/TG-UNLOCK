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

    win_path = ROOT / "windows.py"
    win_text = win_path.read_text(encoding="utf-8")
    win_text = win_text.replace("Local\\\\TgWsProxy_SingleInstance", "Local\\\\TG_UNLOCK_SingleInstance")
    win_path.write_text(win_text, encoding="utf-8", newline="\n")

    locale_dir = ROOT / "ui" / "i18n"
    if not locale_dir.is_dir():
        raise SystemExit("Не найдена папка переводов ui/i18n.")
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
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )

    patch_settings_header()

    spec_path = ROOT / "packaging" / "windows.spec"
    spec = spec_path.read_text(encoding="utf-8")
    spec, count = re.subn(r"(?m)^\s*name=['\"]TgWsProxy['\"],", "    name='TG_UNLOCK',", spec, count=1)
    if count != 1:
        raise SystemExit("Не удалось безопасно изменить имя EXE в packaging/windows.spec.")
    spec_path.write_text(spec, encoding="utf-8", newline="\n")

    print("TG UNLOCK: branding, header, developer contact and donation removal applied.")


if __name__ == "__main__":
    main()
