from __future__ import annotations

import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable


class ZoekenTab:
    """View for the "Zoeken" tab."""

    def __init__(
        self,
        *,
        state,
        connect_db: Callable[[], sqlite3.Connection],
        format_date: Callable[[str], str | None],
        format_datetime_for_display: Callable[[str | None], str],
        auto_adjust_column_width: Callable[[ttk.Treeview, tk.Frame, ttk.Scrollbar], None],
    ) -> None:
        self.state = state
        self._connect_db = connect_db
        self._format_date = format_date
        self._format_datetime_for_display = format_datetime_for_display
        self._auto_adjust_column_width = auto_adjust_column_width

        self.frame = ttk.Frame(self.state.notebook)
        self.state.notebook.add(self.frame, text="Zoeken")

        tk.Label(self.frame, text="Zoek op SIN").grid(
            row=0, column=0, padx=10, pady=5, sticky="w"
        )
        tk.Entry(self.frame, textvariable=self.state.sin_zoek_var).grid(
            row=0, column=1, padx=10, pady=5, sticky="w"
        )

        tk.Label(self.frame, text="Datum van (dd-mm-jjjj)").grid(
            row=1, column=0, padx=10, pady=5, sticky="w"
        )
        tk.Entry(self.frame, textvariable=self.state.datum_vanaf_var).grid(
            row=1, column=1, padx=10, pady=5, sticky="w"
        )

        tk.Label(self.frame, text="Datum tot (dd-mm-jjjj)").grid(
            row=2, column=0, padx=10, pady=5, sticky="w"
        )
        tk.Entry(self.frame, textvariable=self.state.datum_tot_var).grid(
            row=2, column=1, padx=10, pady=5, sticky="w"
        )

        tk.Checkbutton(
            self.frame,
            text="Doorzoek datum_ingave",
            variable=self.state.include_datum_ingave_var,
        ).grid(row=3, column=0, padx=10, pady=5, sticky="w")

        tk.Button(self.frame, text="Zoeken", command=self.zoek_objecten).grid(
            row=3, column=1, padx=10, pady=5, sticky="w"
        )
        tk.Button(self.frame, text="Reset", command=self.reset).grid(
            row=3, column=2, padx=10, pady=5, sticky="w"
        )

        self.tree_frame = tk.Frame(self.frame)
        self.tree_frame.grid(
            row=4, column=0, columnspan=3, padx=10, pady=10, sticky="nsew"
        )

        self.tree_scroll_y = ttk.Scrollbar(self.tree_frame, orient="vertical")
        self.tree_scroll_y.grid(row=0, column=1, sticky="ns")
        self.tree_scroll_x = ttk.Scrollbar(self.tree_frame, orient="horizontal")
        self.tree_scroll_x.grid(row=1, column=0, sticky="ew")

        columns = (
            "id",
            "SIN",
            "Type",
            "Subcategorie",
            "Merk",
            "OS",
            "Dienst",
            "LCCU Lid",
            "Datum in behandeling",
            "Start bijstand",
            "Einde bijstand",
        )
        self.result_tree = ttk.Treeview(
            self.tree_frame,
            columns=columns,
            show="headings",
            displaycolumns=columns[1:],
            yscrollcommand=self.tree_scroll_y.set,
            xscrollcommand=self.tree_scroll_x.set,
        )
        self.result_tree.grid(row=0, column=0, sticky="nsew")
        self.tree_scroll_y.config(command=self.result_tree.yview)
        self.tree_scroll_x.config(command=self.result_tree.xview)
        for col in columns:
            self.result_tree.heading(col, text=col)

        self.frame.grid_rowconfigure(4, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        self.tree_frame.grid_rowconfigure(0, weight=1)
        self.tree_frame.grid_columnconfigure(0, weight=1)

    def zoek_objecten(self) -> None:
        sin = self.state.sin_zoek_var.get()
        datum_vanaf = self._format_date(self.state.datum_vanaf_var.get())
        datum_tot = self._format_date(self.state.datum_tot_var.get())

        query = """
            SELECT
                o.id,
                o.sin,
                o.type,
                o.subcategorie,
                o.merk,
                o.os,
                o.dienst,
                o.lccu_lid,
                o.datum_in_behandeling,
                o.start_bijstand,
                o.einde_bijstand
            FROM objecten o
            WHERE 1=1
        """
        params: list[str] = []

        if sin:
            query += " AND o.sin LIKE ?"
            params.append(f"%{sin}%")

        if datum_vanaf and datum_tot:
            date_conditions = []
            if self.state.include_datum_ingave_var.get():
                date_conditions.append("date(o.datum_ingave) BETWEEN ? AND ?")
                params.extend([datum_vanaf, datum_tot])
            for column in ("datum_in_behandeling", "start_bijstand", "einde_bijstand"):
                date_conditions.append(f"date(o.{column}) BETWEEN ? AND ?")
                params.extend([datum_vanaf, datum_tot])
            query += " AND (" + " OR ".join(date_conditions) + ")"

        try:
            with self._connect_db() as conn:
                cursor = conn.cursor()
                cursor.execute(query, tuple(params))
                results = cursor.fetchall()
        except sqlite3.Error as exc:
            print(f"Databasefout bij zoeken: {exc}")
            messagebox.showerror(
                "Databasefout", f"Fout bij het zoeken: {exc}"
            )
            return

        for row in self.result_tree.get_children():
            self.result_tree.delete(row)

        for row in results:
            row = list(row)
            for index in (8, 9, 10):
                row[index] = self._format_datetime_for_display(row[index])
            self.result_tree.insert("", "end", values=row)

        self.state.root.after(
            100,
            lambda: self._auto_adjust_column_width(
                self.result_tree, self.tree_frame, self.tree_scroll_x
            ),
        )

    def reset(self) -> None:
        self.state.sin_zoek_var.set("")
        self.state.datum_vanaf_var.set("")
        self.state.datum_tot_var.set("")
        for row in self.result_tree.get_children():
            self.result_tree.delete(row)
