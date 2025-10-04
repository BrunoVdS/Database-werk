from __future__ import annotations

import sqlite3
from datetime import datetime
from tkinter import ttk, messagebox
from typing import Callable


class BewerkenTab:
    """View for the "Bewerken" tab."""

    def __init__(
        self,
        *,
        state,
        connect_db: Callable[[], sqlite3.Connection],
        validate_sin: Callable[[str], str],
        parse_dutch_datetime: Callable[[str], datetime],
        parse_dutch_to_iso: Callable[[str], str | None],
        datetime_to_iso: Callable[[datetime], str],
        format_datetime_for_display: Callable[[str | None], str],
        search_callback: Callable[[], None],
        result_tree: ttk.Treeview,
    ) -> None:
        self.state = state
        self._connect_db = connect_db
        self._validate_sin = validate_sin
        self._parse_dutch_datetime = parse_dutch_datetime
        self._parse_dutch_to_iso = parse_dutch_to_iso
        self._datetime_to_iso = datetime_to_iso
        self._format_datetime_for_display = format_datetime_for_display
        self._search_callback = search_callback
        self._current_record_id: str | None = None

        self.frame = ttk.Frame(self.state.notebook)
        self.state.notebook.add(self.frame, text="Bewerken")

        self.state.type_edit_var.trace_add(
            "write", lambda *_: self._update_dropdowns()
        )

        ttk.Label(self.frame, text="SIN-nummer").grid(
            row=0, column=0, padx=10, pady=5, sticky="w"
        )
        ttk.Entry(self.frame, textvariable=self.state.sin_edit_var).grid(
            row=0, column=1, padx=10, pady=5, sticky="w"
        )

        ttk.Label(self.frame, text="Type").grid(
            row=1, column=0, padx=10, pady=5, sticky="w"
        )
        type_frame = ttk.Frame(self.frame)
        type_frame.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        for opt in ("Mobile", "Computer", "Bijstand"):
            ttk.Radiobutton(
                type_frame,
                text=opt,
                variable=self.state.type_edit_var,
                value=opt,
            ).pack(side="left", padx=5)

        ttk.Label(self.frame, text="Subcategorie").grid(
            row=2, column=0, padx=10, pady=5, sticky="w"
        )
        self.subcategorie_dropdown = ttk.Combobox(
            self.frame, textvariable=self.state.subcategorie_edit_var
        )
        self.subcategorie_dropdown.grid(
            row=2, column=1, padx=10, pady=5, sticky="w"
        )

        ttk.Label(self.frame, text="Merk").grid(
            row=3, column=0, padx=10, pady=5, sticky="w"
        )
        ttk.Entry(self.frame, textvariable=self.state.merk_edit_var).grid(
            row=3, column=1, padx=10, pady=5, sticky="w"
        )

        ttk.Label(self.frame, text="Besturingssysteem").grid(
            row=4, column=0, padx=10, pady=5, sticky="w"
        )
        self.os_dropdown = ttk.Combobox(
            self.frame, textvariable=self.state.os_edit_var
        )
        self.os_dropdown.grid(row=4, column=1, padx=10, pady=5, sticky="w")

        ttk.Label(self.frame, text="Dienst").grid(
            row=5, column=0, padx=10, pady=5, sticky="w"
        )
        ttk.Entry(self.frame, textvariable=self.state.dienst_edit_var).grid(
            row=5, column=1, padx=10, pady=5, sticky="w"
        )

        ttk.Label(self.frame, text="Soort bijstand").grid(
            row=6, column=0, padx=10, pady=5, sticky="w"
        )
        ttk.Entry(self.frame, textvariable=self.state.soort_bijstand_edit_var).grid(
            row=6, column=1, padx=10, pady=5, sticky="w"
        )

        ttk.Label(self.frame, text="LCCU lid").grid(
            row=7, column=0, padx=10, pady=5, sticky="w"
        )
        ttk.Entry(self.frame, textvariable=self.state.lccu_lid_edit_var).grid(
            row=7, column=1, padx=10, pady=5, sticky="w"
        )

        ttk.Checkbutton(
            self.frame,
            text="Datum in behandeling",
            variable=self.state.datum_in_behandeling_checkbox_var,
            command=self._toggle_datum_in_behandeling,
        ).grid(row=8, column=0, padx=10, pady=5, sticky="w")
        ttk.Entry(
            self.frame,
            textvariable=self.state.datum_in_behandeling_edit_var,
        ).grid(row=8, column=1, padx=10, pady=5, sticky="w")

        ttk.Label(self.frame, text="Start bijstand (dd-mm-jjjj uu:mm)").grid(
            row=9, column=0, padx=10, pady=5, sticky="w"
        )
        ttk.Entry(self.frame, textvariable=self.state.start_bijstand_edit_var).grid(
            row=9, column=1, padx=10, pady=5, sticky="w"
        )

        ttk.Label(self.frame, text="Einde bijstand (dd-mm-jjjj uu:mm)").grid(
            row=10, column=0, padx=10, pady=5, sticky="w"
        )
        ttk.Entry(self.frame, textvariable=self.state.einde_bijstand_edit_var).grid(
            row=10, column=1, padx=10, pady=5, sticky="w"
        )

        ttk.Button(self.frame, text="Opslaan", command=self.update_record).grid(
            row=11, column=1, pady=10
        )

        self.result_tree = result_tree
        self.result_tree.bind("<Double-1>", self.load_record_for_edit)

    def _update_dropdowns(self) -> None:
        tab_type = self.state.type_edit_var.get()
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
        else:
            self.subcategorie_dropdown["values"] = []
            self.os_dropdown["values"] = []

    def _toggle_datum_in_behandeling(self) -> None:
        if self.state.datum_in_behandeling_checkbox_var.get():
            self.state.datum_in_behandeling_edit_var.set(
                datetime.now().strftime("%d-%m-%Y %H:%M")
            )
        else:
            self.state.datum_in_behandeling_edit_var.set("")

    def update_record(self) -> None:
        if not self._current_record_id:
            messagebox.showwarning("Fout", "Geen record geselecteerd.")
            return

        datum_in_behandeling_input = (
            self.state.datum_in_behandeling_edit_var.get().strip()
        )
        start_input = self.state.start_bijstand_edit_var.get().strip()
        einde_input = self.state.einde_bijstand_edit_var.get().strip()

        if (
            self.state.datum_in_behandeling_checkbox_var.get()
            and not datum_in_behandeling_input
        ):
            messagebox.showerror(
                "Fout", "Datum in behandeling mag niet leeg zijn."
            )
            return

        try:
            start_dt = (
                self._parse_dutch_datetime(start_input)
                if start_input
                else None
            )
            einde_dt = (
                self._parse_dutch_datetime(einde_input)
                if einde_input
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

        if self.state.datum_in_behandeling_checkbox_var.get():
            try:
                datum_in_behandeling_iso = self._parse_dutch_to_iso(
                    datum_in_behandeling_input
                )
            except ValueError:
                messagebox.showerror(
                    "Fout", "Ongeldig datumformaat! Gebruik: dd-mm-jjjj uu:mm"
                )
                return
        else:
            datum_in_behandeling_iso = None

        start_bijstand_iso = (
            self._datetime_to_iso(start_dt) if start_dt else None
        )
        einde_bijstand_iso = (
            self._datetime_to_iso(einde_dt) if einde_dt else None
        )

        sin_input = self.state.sin_edit_var.get()
        try:
            normalized_sin = self._validate_sin(sin_input)
        except ValueError as exc:
            messagebox.showerror("Fout", str(exc))
            return

        self.state.sin_edit_var.set(normalized_sin)
        is_bijstand_record = (
            self.state.type_edit_var.get().strip().lower() == "bijstand"
            or normalized_sin == "BIJSTAND"
        )

        try:
            with self._connect_db() as conn:
                cursor = conn.cursor()
                medewerkers_for_bijstand: list[str] = []
                if is_bijstand_record:
                    cursor.execute(
                        "SELECT medewerker FROM medewerkers_bijstand WHERE object_id = ?",
                        (self._current_record_id,),
                    )
                    medewerkers_for_bijstand = [row[0] for row in cursor.fetchall()]

                cursor.execute(
                    """
                    UPDATE objecten SET
                        sin = ?,
                        type = ?,
                        subcategorie = ?,
                        merk = ?,
                        os = ?,
                        dienst = ?,
                        soort_bijstand = ?,
                        lccu_lid = ?,
                        datum_in_behandeling = ?,
                        start_bijstand = ?,
                        einde_bijstand = ?
                    WHERE id = ?
                    """,
                    (
                        normalized_sin,
                        self.state.type_edit_var.get(),
                        self.state.subcategorie_edit_var.get(),
                        self.state.merk_edit_var.get(),
                        self.state.os_edit_var.get(),
                        self.state.dienst_edit_var.get(),
                        self.state.soort_bijstand_edit_var.get(),
                        self.state.lccu_lid_edit_var.get(),
                        datum_in_behandeling_iso,
                        start_bijstand_iso,
                        einde_bijstand_iso,
                        self._current_record_id,
                    ),
                )

                if is_bijstand_record:
                    cursor.execute(
                        "DELETE FROM medewerkers_bijstand WHERE object_id = ?",
                        (self._current_record_id,),
                    )
                    for medewerker_name in medewerkers_for_bijstand:
                        cursor.execute(
                            """
                            INSERT INTO medewerkers_bijstand (
                                object_id,
                                medewerker,
                                start_bijstand,
                                einde_bijstand
                            )
                            VALUES (?, ?, ?, ?)
                            """,
                            (
                                self._current_record_id,
                                medewerker_name,
                                start_bijstand_iso,
                                einde_bijstand_iso,
                            ),
                        )
                    cursor.execute(
                        "UPDATE objecten SET aantal_medewerkers = ? WHERE id = ?",
                        (len(medewerkers_for_bijstand), self._current_record_id),
                    )
        except sqlite3.Error as exc:
            print(f"Databasefout bij bijwerken: {exc}")
            messagebox.showerror(
                "Databasefout", f"Fout bij het bijwerken: {exc}"
            )
            return

        success_message = "Record bijgewerkt!"
        if is_bijstand_record:
            success_message += (
                "\n\nTODO: Aanpassen van de medewerkerslijst is nog niet beschikbaar in dit scherm."
            )
        messagebox.showinfo("Succes", success_message)
        self._search_callback()

    def load_record_for_edit(self, _event) -> None:
        selected = self.result_tree.focus()
        if not selected:
            return
        values = self.result_tree.item(selected, "values")
        if not values:
            return

        self._current_record_id = values[0]
        sin_value = values[1]
        type_value = values[2]
        valid_types = {"Mobile", "Computer", "Bijstand"}
        is_bijstand_record = sin_value == "BIJSTAND" or type_value not in valid_types
        normalized_type = "Bijstand" if is_bijstand_record else type_value

        self.state.sin_edit_var.set(sin_value)
        self.state.type_edit_var.set(normalized_type or "")
        self.state.subcategorie_edit_var.set(values[3])
        self.state.merk_edit_var.set(values[4])
        self.state.os_edit_var.set(values[5])
        self.state.dienst_edit_var.set(values[6])
        self.state.lccu_lid_edit_var.set(values[7])

        if is_bijstand_record:
            soort_bijstand_value = ""
            try:
                with self._connect_db() as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "SELECT soort_bijstand FROM objecten WHERE id = ?",
                        (self._current_record_id,),
                    )
                    result = cursor.fetchone()
                if result:
                    soort_bijstand_value = result[0] or ""
            except sqlite3.Error as exc:
                print(f"Databasefout bij ophalen bijstand: {exc}")
                soort_bijstand_value = ""
            self.state.soort_bijstand_edit_var.set(soort_bijstand_value)
        else:
            self.state.soort_bijstand_edit_var.set("")

        has_datum_in_behandeling = bool(values[8])
        self.state.datum_in_behandeling_edit_var.set(
            self._format_datetime_for_display(values[8])
        )
        self.state.start_bijstand_edit_var.set(
            self._format_datetime_for_display(values[9])
        )
        self.state.einde_bijstand_edit_var.set(
            self._format_datetime_for_display(values[10])
        )
        self.state.datum_in_behandeling_checkbox_var.set(
            has_datum_in_behandeling
        )
        self.state.notebook.select(self.frame)
