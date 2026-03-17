import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import os
import json
from pathlib import Path

import re
import metadata as meta_module
from metadata import extract_text_from_pdf, get_pdf_metadata
from utils import format_filename, rename_file

# ── Settings persistence (macOS convention) ────────────────────────────────────
SETTINGS_DIR = Path.home() / "Library" / "Application Support" / "RenamerUI"
SETTINGS_FILE = SETTINGS_DIR / "settings.json"


def load_settings() -> dict:
    if SETTINGS_FILE.exists():
        with open(SETTINGS_FILE) as f:
            return json.load(f)

    # First run: migrate API key from .env if present
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        try:
            from dotenv import dotenv_values
            key = dotenv_values(env_path).get("GOOGLE_API_KEY", "")
            if key and key != "your_gemini_api_key_here":
                return {"api_key": key}
        except Exception:
            pass
    return {"api_key": ""}


def save_settings(data: dict):
    SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
    with open(SETTINGS_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ── Settings dialog ────────────────────────────────────────────────────────────

class SettingsDialog(ctk.CTkToplevel):
    def __init__(self, parent, current_api_key: str):
        super().__init__(parent)
        self.title("Instellingen")
        self.geometry("500x190")
        self.resizable(False, False)
        self.grab_set()

        self.result = None
        self.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            self, text="Google Gemini API Key:", anchor="w",
            font=ctk.CTkFont(size=13)
        ).grid(row=0, column=0, padx=(24, 10), pady=(32, 8), sticky="w")

        self._key_var = ctk.StringVar(value=current_api_key)
        self._key_entry = ctk.CTkEntry(
            self, textvariable=self._key_var,
            width=260, show="•", font=ctk.CTkFont(size=13)
        )
        self._key_entry.grid(row=0, column=1, padx=(0, 10), pady=(32, 8), sticky="ew")

        self._show_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            self, text="Toon",
            variable=self._show_var,
            command=self._toggle_show,
            width=70
        ).grid(row=0, column=2, padx=(0, 24), pady=(32, 8))

        ctk.CTkLabel(
            self,
            text="Sleutel aanmaken via aistudio.google.com/app/apikey",
            text_color="gray", font=ctk.CTkFont(size=11), anchor="w"
        ).grid(row=1, column=0, columnspan=3, padx=24, sticky="w")

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=2, column=0, columnspan=3, pady=(16, 24), padx=24, sticky="e")

        ctk.CTkButton(
            btn_frame, text="Annuleer", width=110,
            fg_color="transparent", border_width=1,
            command=self.destroy
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            btn_frame, text="Opslaan", width=110,
            command=self._save
        ).pack(side="left")

    def _toggle_show(self):
        self._key_entry.configure(show="" if self._show_var.get() else "•")

    def _save(self):
        self.result = self._key_var.get().strip()
        self.destroy()


# ── Main application ───────────────────────────────────────────────────────────

class RenamerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("RenamerUI")
        self.geometry("660x580")
        self.minsize(540, 500)

        self._settings = load_settings()
        meta_module.initialize_client(self._settings.get("api_key", ""))

        self._folder = ctk.StringVar(value="")
        self._dry_run = ctk.BooleanVar(value=False)

        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(24, 0))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header, text="RenamerUI",
            font=ctk.CTkFont(size=24, weight="bold")
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            header, text="AI-gestuurd PDF-hernoemingsprogramma",
            text_color="gray", font=ctk.CTkFont(size=13)
        ).grid(row=1, column=0, sticky="w")

        ctk.CTkButton(
            header, text="⚙  Instellingen",
            width=140, height=32,
            fg_color="transparent", border_width=1,
            font=ctk.CTkFont(size=13),
            command=self._open_settings
        ).grid(row=0, column=1, rowspan=2, sticky="e")

        # Divider
        ctk.CTkFrame(self, height=1, fg_color="gray30").grid(
            row=1, column=0, sticky="ew", padx=24, pady=18
        )

        # Controls
        ctrl = ctk.CTkFrame(self, fg_color="transparent")
        ctrl.grid(row=2, column=0, sticky="ew", padx=24)
        ctrl.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            ctrl, text="Map selecteren",
            font=ctk.CTkFont(size=14, weight="bold"), anchor="w"
        ).grid(row=0, column=0, sticky="w", pady=(0, 10))

        folder_row = ctk.CTkFrame(ctrl, fg_color="transparent")
        folder_row.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        folder_row.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            folder_row, text="📁  Kies map…",
            width=130, height=38,
            font=ctk.CTkFont(size=13),
            command=self._pick_folder
        ).grid(row=0, column=0, padx=(0, 12))

        ctk.CTkLabel(
            folder_row, textvariable=self._folder,
            anchor="w", text_color="gray",
            font=ctk.CTkFont(size=12)
        ).grid(row=0, column=1, sticky="ew")

        ctk.CTkLabel(
            ctrl, text="Opties",
            font=ctk.CTkFont(size=14, weight="bold"), anchor="w"
        ).grid(row=2, column=0, sticky="w", pady=(0, 10))

        ctk.CTkCheckBox(
            ctrl,
            text="Dry-run  —  toon welke namen gebruikt zouden worden, zonder te hernoemen",
            variable=self._dry_run,
            font=ctk.CTkFont(size=13)
        ).grid(row=3, column=0, sticky="w", pady=(0, 22))

        self._start_btn = ctk.CTkButton(
            ctrl,
            text="▶  Start hernoeming",
            height=46,
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self._start
        )
        self._start_btn.grid(row=4, column=0, sticky="ew")

        self._progress = ctk.CTkProgressBar(ctrl, mode="indeterminate")
        self._progress.grid(row=5, column=0, sticky="ew", pady=(10, 0))
        self._progress.grid_remove()

        # Log area
        log_frame = ctk.CTkFrame(self, fg_color="transparent")
        log_frame.grid(row=3, column=0, sticky="nsew", padx=24, pady=(18, 0))
        log_frame.grid_columnconfigure(0, weight=1)
        log_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            log_frame, text="Logboek",
            font=ctk.CTkFont(size=14, weight="bold"), anchor="w"
        ).grid(row=0, column=0, sticky="w", pady=(0, 6))

        self._log_box = ctk.CTkTextbox(
            log_frame,
            font=ctk.CTkFont(family="Menlo", size=12),
            activate_scrollbars=True,
            state="disabled"
        )
        self._log_box.grid(row=1, column=0, sticky="nsew")

        # Status bar
        self._status_var = ctk.StringVar(value="Klaar om te starten")
        ctk.CTkLabel(
            self, textvariable=self._status_var,
            text_color="gray", font=ctk.CTkFont(size=11), anchor="w"
        ).grid(row=4, column=0, sticky="ew", padx=26, pady=(6, 16))

    # ── Event handlers ─────────────────────────────────────────────────────

    def _pick_folder(self):
        path = filedialog.askdirectory(title="Selecteer map met PDF-bestanden")
        if path:
            self._folder.set(path)

    def _open_settings(self):
        dlg = SettingsDialog(self, self._settings.get("api_key", ""))
        self.wait_window(dlg)
        if dlg.result is not None:
            self._settings["api_key"] = dlg.result
            save_settings(self._settings)
            meta_module.initialize_client(dlg.result)
            self._log("✓ Instellingen opgeslagen.")

    def _start(self):
        folder = self._folder.get()

        if not folder:
            messagebox.showwarning("Geen map geselecteerd", "Selecteer eerst een map met PDF-bestanden.")
            return
        if not os.path.isdir(folder):
            messagebox.showerror("Ongeldige map", f"'{folder}' is geen geldige map.")
            return
        if not self._settings.get("api_key"):
            messagebox.showerror(
                "API Key ontbreekt",
                "Stel eerst een Google Gemini API key in via de knop 'Instellingen'."
            )
            return

        self._log_box.configure(state="normal")
        self._log_box.delete("1.0", "end")
        self._log_box.configure(state="disabled")

        self._start_btn.configure(state="disabled")
        self._progress.grid()
        self._progress.start()
        self._status_var.set("Bezig met verwerken…")

        threading.Thread(
            target=self._process_folder,
            args=(folder, self._dry_run.get()),
            daemon=True
        ).start()

    # ── Background worker ──────────────────────────────────────────────────

    def _process_folder(self, folder: str, dry_run: bool):
        pdf_files = sorted(f for f in os.listdir(folder) if f.lower().endswith(".pdf"))

        if not pdf_files:
            self._log("Geen PDF-bestanden gevonden in de geselecteerde map.")
            self._finish("Klaar — geen PDF-bestanden gevonden")
            return

        prefix = "[DRY-RUN]  " if dry_run else ""
        self._log(f"{prefix}Verwerken van {len(pdf_files)} PDF-bestand(en) in:\n{folder}\n{'─' * 60}")

        renamed = 0
        failed = 0
        skipped = 0
        _already_named = re.compile(r'^\d{4}-\d{2} - .+ - .+\.pdf$')

        for filename in pdf_files:
            file_path = os.path.join(folder, filename)

            if _already_named.match(filename):
                self._log(f"\n⏭  {filename}\n   —  al correct opgemaakt, overgeslagen")
                skipped += 1
                continue

            self._log(f"\n⟳  {filename}")

            text = extract_text_from_pdf(file_path)
            if not text:
                self._log("   ✗  Geen tekst gevonden in dit bestand")
                failed += 1
                continue

            md = get_pdf_metadata(text)
            if not md:
                self._log("   ✗  Kon geen metadata ophalen via Gemini")
                failed += 1
                continue

            new_name = format_filename(md)

            if dry_run:
                self._log(f"   →  {new_name}")
            else:
                new_path = rename_file(file_path, new_name)
                if new_path:
                    self._log(f"   ✓  {os.path.basename(new_path)}")
                    renamed += 1
                else:
                    self._log("   ✗  Hernoemen mislukt")
                    failed += 1

        self._log(f"\n{'─' * 60}")
        if dry_run:
            summary = f"Dry-run voltooid — {len(pdf_files) - skipped} geanalyseerd, {skipped} overgeslagen"
        else:
            summary = f"Klaar — {renamed} hernoemd, {skipped} overgeslagen, {failed} mislukt"
        self._log(f"✓  {summary}")
        self._finish(summary)

    # ── UI helpers (thread-safe) ───────────────────────────────────────────

    def _log(self, msg: str):
        def _update():
            self._log_box.configure(state="normal")
            self._log_box.insert("end", msg + "\n")
            self._log_box.see("end")
            self._log_box.configure(state="disabled")
        self.after(0, _update)

    def _finish(self, status: str = "Klaar"):
        def _update():
            self._start_btn.configure(state="normal")
            self._progress.stop()
            self._progress.grid_remove()
            self._status_var.set(status)
        self.after(0, _update)


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    ctk.set_appearance_mode("system")
    ctk.set_default_color_theme("blue")
    app = RenamerApp()
    app.mainloop()
