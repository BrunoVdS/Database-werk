from __future__ import annotations

import sqlite3
import tkinter as tk
from datetime import datetime
from tkinter import ttk, messagebox
from typing import Callable, Sequence


class BijstandPopup:
    """Encapsulates the bijstand popup window."""

    def __init__(
        self,
        *,
        state,
        medewerkers: Sequence[str],
        diensten: Sequence[str],
        parse_dutch_datetime: Callable[[str], datetime],
        datetime_to_iso: Callable[[datetime], str],
        current_timestamp: Callable[[], str],
        insert_bijstand_record: Callable[..., int],
    ) -> None:
        self.state = state
        self._medewerkers = medewerkers
        self._diensten = diensten
        self._parse_dutch_datetime = parse_dutch_datetime
        self._datetime_to_iso = datetime_to_iso
        self._current_timestamp = current_timestamp
        self._insert_bijstand_record = insert_bijstand_record

    def open(self) -> None:
        if (
            self.state.popup_window is not None
            and self.state.popup_window.winfo_exists()
        ):
            self.state.popup_window.destroy()

        self.state.popup_window = tk.Toplevel(self.state.root)
        self.state.popup_window.title("Bijstand ingeven")
        self.state.popup_window.geometry("400x600")

        self.state.soort_bijstand_var.set("")
        self.state.aantal_medewerkers_var.set("")
        self.state.start_bijstand_var.set("")
        self.state.einde_bijstand_var.set("")
        self.state.medewerker_widgets.clear()

        tk.Label(self.state.popup_window, text="Soort bijstand").pack(pady=5)
        ttk.Combobox(
            self.state.popup_window,
            textvariable=self.state.soort_bijstand_var,
            values=["Camerabeelden", "Huiszoeking", "Wacht", "Andere"],
        ).pack(pady=5)

        tk.Label(
            self.state.popup_window, text="Aantal medewerkers LCCU"
        ).pack(pady=5)
        tk.Entry(
            self.state.popup_window,
            textvariable=self.state.aantal_medewerkers_var,
        ).pack(pady=5)

        medewerkers_frame = tk.Frame(self.state.popup_window)
        medewerkers_frame.pack(pady=5)

        def update_medewerkers(*_args):
            if not medewerkers_frame.winfo_exists():
                return
            for widget in medewerkers_frame.winfo_children():
                widget.destroy()
            value = self.state.aantal_medewerkers_var.get().strip()
            aantal_medewerkers = int(value) if value.isdigit() else 0
            self.state.medewerker_widgets.clear()
            for index in range(aantal_medewerkers):
                tk.Label(
                    medewerkers_frame, text=f"Medewerker {index + 1}"
                ).grid(row=index, column=0, padx=5, pady=2)
                medewerker_combobox = ttk.Combobox(
                    medewerkers_frame, values=self._medewerkers
                )
                medewerker_combobox.grid(row=index, column=1, padx=5, pady=2)
                self.state.medewerker_widgets.append(medewerker_combobox)

        if self.state._medewerkers_trace_id is not None:
            self.state.aantal_medewerkers_var.trace_remove(
                "write", self.state._medewerkers_trace_id
            )
        self.state._medewerkers_trace_id = self.state.aantal_medewerkers_var.trace_add(
            "write", update_medewerkers
        )

        tk.Label(self.state.popup_window, text="Dienst").pack(pady=5)
        ttk.Combobox(
            self.state.popup_window,
            textvariable=self.state.dienst_var,
            values=self._diensten,
        ).pack(pady=5)

        tk.Label(
            self.state.popup_window, text="Start bijstand (dd-mm-jjjj uu:mm)"
        ).pack(pady=5)
        tk.Entry(
            self.state.popup_window, textvariable=self.state.start_bijstand_var
        ).pack(pady=5)

        tk.Label(
            self.state.popup_window, text="Einde bijstand (dd-mm-jjjj uu:mm)"
        ).pack(pady=5)
        tk.Entry(
            self.state.popup_window, textvariable=self.state.einde_bijstand_var
        ).pack(pady=5)

        tk.Button(
            self.state.popup_window, text="Opslaan", command=self.save
        ).pack(pady=10)
        self.state.popup_window.protocol("WM_DELETE_WINDOW", self.close)

    def close(self) -> None:
        if self.state.popup_window:
            self.state.popup_window.destroy()
            self.state.popup_window = None

    def save(self) -> None:
        soort_bijstand = self.state.soort_bijstand_var.get()
        medewerkers_list = [w.get() for w in self.state.medewerker_widgets]
        start_input = self.state.start_bijstand_var.get()
        einde_input = self.state.einde_bijstand_var.get()

        try:
            start_dt = (
                self._parse_dutch_datetime(start_input)
                if start_input and start_input.strip()
                else None
            )
            einde_dt = (
                self._parse_dutch_datetime(einde_input)
                if einde_input and einde_input.strip()
                else None
            )
        except ValueError:
            messagebox.showerror(
                "Fout", "Ongeldig datumformaat! Gebruik: dd-mm-jjjj uu:mm"
            )
            return

        if start_dt and einde_dt and einde_dt < start_dt:
            messagebox.showerror(
                "Fout", "Einde bijstand mag niet voor Start bijstand zijn!"
            )
            return

        start_bijstand = (
            self._datetime_to_iso(start_dt) if start_dt is not None else None
        )
        einde_bijstand = (
            self._datetime_to_iso(einde_dt) if einde_dt is not None else None
        )

        try:
            datum_ingave = self._current_timestamp()
            self._insert_bijstand_record(
                soort_bijstand=soort_bijstand,
                dienst=self.state.dienst_var.get(),
                medewerkers=medewerkers_list,
                start_bijstand=start_bijstand,
                einde_bijstand=einde_bijstand,
                datum_ingave=datum_ingave,
            )
        except sqlite3.Error as exc:
            print(f"Databasefout bij opslaan bijstand: {exc}")
            messagebox.showerror(
                "Databasefout",
                f"Fout bij het opslaan in de database: {exc}",
            )
            return

        messagebox.showinfo("Succes", "Bijstand succesvol opgeslagen!")
        self.close()
