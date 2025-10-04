from __future__ import annotations

import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Sequence


class IngaveTab:
    """View for the "Ingave" tab."""

    def __init__(
        self,
        *,
        state,
        diensten: Sequence[str],
        validate_sin: Callable[[str], str],
        connect_db: Callable[[], sqlite3.Connection],
        current_timestamp: Callable[[], str],
        popup,
    ) -> None:
        self.state = state
        self._diensten = diensten
        self._validate_sin = validate_sin
        self._connect_db = connect_db
        self._current_timestamp = current_timestamp
        self._popup = popup

        self.frame = ttk.Frame(self.state.notebook)
        self.state.notebook.add(self.frame, text="Ingave")

        self.state.sin_var.trace_add("write", self._update_sin)
        self.state.type_var.trace_add("write", lambda *_: self._update_picklists())

        tk.Label(self.frame, text="SIN-nummer").grid(
            row=0, column=0, padx=10, pady=5, sticky="w"
        )
        tk.Entry(self.frame, textvariable=self.state.sin_var).grid(
            row=0, column=1, padx=10, pady=5, sticky="w"
        )

        tk.Label(self.frame, text="Type").grid(
            row=1, column=0, padx=10, pady=5, sticky="w"
        )
        type_frame = tk.Frame(self.frame)
        type_frame.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        for opt in ("Mobile", "Computer", "Bijstand"):
            tk.Radiobutton(
                type_frame,
                text=opt,
                variable=self.state.type_var,
                value=opt,
                command=self._update_picklists,
            ).pack(side="left", padx=5)

        tk.Label(self.frame, text="Subcategorie").grid(
            row=2, column=0, padx=10, pady=5, sticky="w"
        )
        self.subcategorie_dropdown = ttk.Combobox(
            self.frame, textvariable=self.state.subcategorie_var
        )
        self.subcategorie_dropdown.grid(
            row=2, column=1, padx=10, pady=5, sticky="w"
        )

        tk.Label(self.frame, text="Merk").grid(
            row=3, column=0, padx=10, pady=5, sticky="w"
        )
        tk.Entry(self.frame, textvariable=self.state.merk_var).grid(
            row=3, column=1, padx=10, pady=5, sticky="w"
        )

        tk.Label(self.frame, text="Besturingssysteem").grid(
            row=4, column=0, padx=10, pady=5, sticky="w"
        )
        self.os_dropdown = ttk.Combobox(
            self.frame, textvariable=self.state.os_var
        )
        self.os_dropdown.grid(row=4, column=1, padx=10, pady=5, sticky="w")

        tk.Label(self.frame, text="Dienst").grid(
            row=5, column=0, padx=10, pady=5, sticky="w"
        )
        ttk.Combobox(
            self.frame,
            textvariable=self.state.dienst_var,
            values=self._diensten,
            state="readonly",
        ).grid(row=5, column=1, padx=10, pady=5, sticky="w")

        tk.Button(self.frame, text="Opslaan", command=self._save).grid(
            row=6, column=1, pady=10, sticky="w"
        )
        tk.Button(self.frame, text="Reset", command=self._reset).grid(
            row=6, column=2, pady=10, sticky="w"
        )

        self._update_picklists()

    def _update_sin(self, *_args) -> None:
        value = self.state.sin_var.get().upper()
        if len(value) > 8:
            value = value[:8]
        if value != self.state.sin_var.get():
            self.state.sin_var.set(value)

    def _update_picklists(self) -> None:
        tab_type = self.state.type_var.get()
        if tab_type == "Mobile":
            self.subcategorie_dropdown["values"] = [
                "GSM",
                "Tablet",
                "Sim",
                "SD-kaart",
                "USB-drive",
                "Andere",
            ]
            self.os_dropdown["values"] = [
                "Android",
                "GrapheneOS",
                "iOS",
                "Andere",
            ]
        elif tab_type == "Computer":
            self.subcategorie_dropdown["values"] = [
                "Laptop",
                "Desktop",
                "Losse HD",
                "Andere",
            ]
            self.os_dropdown["values"] = [
                "Windows",
                "Linux",
                "MacOS",
                "Chromebook",
                "Andere",
            ]
        elif tab_type == "Bijstand":
            self._popup.open()
        else:
            self.subcategorie_dropdown["values"] = []
            self.os_dropdown["values"] = []
        self.state.subcategorie_var.set("")
        self.state.os_var.set("")

    def _reset(self) -> None:
        self.state.sin_var.set("")
        self.state.type_var.set("Mobile")
        self.state.subcategorie_var.set("")
        self.state.merk_var.set("")
        self.state.os_var.set("")
        self.state.dienst_var.set("")

    def _save(self) -> None:
        sin = self.state.sin_var.get().strip()
        tab_type = self.state.type_var.get()
        if tab_type == "Bijstand":
            messagebox.showinfo(
                "Informatie", "Gebruik de popup voor bijstandgegevens."
            )
            return

        try:
            normalized_sin = self._validate_sin(sin)
        except ValueError as exc:
            messagebox.showerror("Fout", str(exc))
            return

        subcategorie = self.state.subcategorie_var.get()
        merk = self.state.merk_var.get()
        os_value = self.state.os_var.get()
        dienst = self.state.dienst_var.get()
        datum_ingave = self._current_timestamp()
        unique_id = None

        try:
            with self._connect_db() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO objecten (sin, type, subcategorie, merk, os, dienst, datum_ingave, unique_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        normalized_sin,
                        tab_type,
                        subcategorie,
                        merk,
                        os_value,
                        dienst,
                        datum_ingave,
                        unique_id,
                    ),
                )
        except sqlite3.Error as exc:
            print(f"Databasefout bij opslaan: {exc}")
            messagebox.showerror(
                "Databasefout", f"Fout bij het opslaan: {exc}"
            )
            return

        messagebox.showinfo("Succes", "Gegevens succesvol opgeslagen!")
        self._reset()
