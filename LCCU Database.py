import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import sys
import os
import random
import tkinter.font as tkFont
from typing import Sequence

from config import get_database_path


def resource_path(relative_path):
    """Get absolute path to resource (compatible met PyInstaller onefile)."""
    try:
        base_path = sys._MEIPASS  # PyInstaller sets this in onefile mode
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# --- DATABASE SETUP ---


def connect_db():
    db_path = get_database_path()
    try:
        return sqlite3.connect(db_path)
    except sqlite3.Error as exc:
        raise sqlite3.OperationalError(
            "Kan geen verbinding maken met de database op "
            f"'{db_path}'. Controleer de netwerkverbinding of pas de configuratie aan."
        ) from exc


def _normalize_datetime_value(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    if not value:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%d-%m-%Y %H:%M", "%d-%m-%Y %H:%M:%S"):
        try:
            dt = datetime.strptime(value, fmt)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue
    return value


def normalize_datetime_fields():
    conn: sqlite3.Connection | None = None
    try:
        conn = connect_db()
        cursor = conn.cursor()
        columns = [
            "datum_in_behandeling",
            "start_bijstand",
            "einde_bijstand",
        ]
        for column in columns:
            cursor.execute(
                f"SELECT id, {column} FROM objecten WHERE {column} IS NOT NULL AND TRIM({column}) != ''"
            )
            rows = cursor.fetchall()
            for object_id, value in rows:
                normalized = _normalize_datetime_value(value)
                if normalized and normalized != value:
                    cursor.execute(
                        f"UPDATE objecten SET {column} = ? WHERE id = ?",
                        (normalized, object_id),
                    )
        conn.commit()
    except sqlite3.Error as e:
        print(f"Kon datums niet normaliseren: {e}")
    finally:
        if conn is not None:
            conn.close()


def create_table():
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS objecten (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sin TEXT NOT NULL,
                type TEXT,
                subcategorie TEXT,
                merk TEXT,
                os TEXT,
                dienst TEXT,
                datum_ingave TEXT,
                unique_id INTEGER,
                soort_bijstand TEXT,
                lccu_lid TEXT,
                datum_in_behandeling TEXT,
                aantal_medewerkers INTEGER,
                start_bijstand TEXT,
                einde_bijstand TEXT
            );
            """
        )
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        messagebox.showerror(
            "Databasefout", f"Fout bij het aanmaken van de tabel: {e}"
        )


def create_medewerkers_bijstand_table():
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS medewerkers_bijstand (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                object_id INTEGER,
                medewerker TEXT,
                start_bijstand TEXT,
                einde_bijstand TEXT,
                FOREIGN KEY(object_id) REFERENCES objecten(id)
            );
            """
        )
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        messagebox.showerror(
            "Databasefout",
            f"Fout bij het aanmaken van de medewerkers_bijstand tabel: {e}",
        )


def check_or_create_database():
    create_table()
    create_medewerkers_bijstand_table()
    normalize_datetime_fields()


def insert_bijstand_record(
    *,
    soort_bijstand: str,
    dienst: str,
    medewerkers: Sequence[str],
    start_bijstand: str | None,
    einde_bijstand: str | None,
    sin: str = "BIJSTAND",
    datum_ingave: str | None = None,
    unique_id: int | None = None,
) -> int:
    """Insert a bijstand record and return the created object ID.

    This helper mirrors the logic that is triggered from the GUI popup but keeps
    it accessible for testing so we can verify database behaviour without a
    graphical environment.
    """

    if datum_ingave is None:
        datum_ingave = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if unique_id is None:
        unique_id = random.randint(1000, 9999)

    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO objecten (
                sin,
                type,
                subcategorie,
                merk,
                os,
                dienst,
                datum_ingave,
                unique_id,
                soort_bijstand,
                aantal_medewerkers,
                start_bijstand,
                einde_bijstand
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                sin,
                "Bijstand",
                "",
                "",
                "",
                dienst,
                datum_ingave,
                unique_id,
                soort_bijstand,
                len(medewerkers),
                start_bijstand,
                einde_bijstand,
            ),
        )
        object_id = cursor.lastrowid
        for medewerker in medewerkers:
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
                (object_id, medewerker, start_bijstand, einde_bijstand),
            )
    return object_id


# --- HOOFD VARIABELEN ---
diensten = [
    "DOT",
    "FGP",
    "GOK",
    "GOUDI",
    "INTEL",
    "InternToezicht",
    "ISRA",
    "LR/DGV",
    "LR/DGWLD",
    "LR/DRUGS",
    "LR/ECOFIN",
    "LR/EIG",
    "LR/GWLD",
    "LR/IFG",
    "LR/JCRIM",
    "LR/JEUGD",
    "LR/LM",
    "LR/PERS",
    "LR/PERS/DGV",
    "LR/RESID",
    "LR/RIF",
    "LR/VERDW",
    "LR/ZEDEN",
    "ORIDA",
    "PTA",
    "VERKEER",
    "WIJK Centrum",
    "WIJK City",
    "WIJK Noord",
    "WIJK Oost",
    "WIJK West",
    "WIJK Zuid",
    "WOT Centrum",
    "WOT City",
    "WOT Noord",
    "WOT Oost",
    "WOT West",
    "WOT Zuid",
]

medewerkers = [
    "Annik Van Herck",
    "Bianca Van Loock",
    "Bjorn Broeckx",
    "Bruno Van Der Straten",
    "Carla Winkelmans",
    "Ellen Nuyens",
    "Joeri Haepers",
    "Sabrina Vunckx",
]


class GUIState:
    """Centrale opslag voor Tk widgets en variabelen."""

    def __init__(self, master: tk.Misc | None = None):
        self.root = master or tk.Tk()
        self.notebook = ttk.Notebook(self.root)

        # Variabelen Ingave
        self.sin_var = tk.StringVar(master=self.root)
        self.type_var = tk.StringVar(master=self.root, value="Mobile")
        self.subcategorie_var = tk.StringVar(master=self.root)
        self.merk_var = tk.StringVar(master=self.root)
        self.os_var = tk.StringVar(master=self.root)
        self.dienst_var = tk.StringVar(master=self.root)

        # Variabelen Zoeken
        self.sin_zoek_var = tk.StringVar(master=self.root)
        self.datum_vanaf_var = tk.StringVar(master=self.root)
        self.datum_tot_var = tk.StringVar(master=self.root)
        self.include_datum_ingave_var = tk.BooleanVar(master=self.root, value=True)

        # Variabelen Bewerken
        self.sin_edit_var = tk.StringVar(master=self.root)
        self.type_edit_var = tk.StringVar(master=self.root)
        self.subcategorie_edit_var = tk.StringVar(master=self.root)
        self.merk_edit_var = tk.StringVar(master=self.root)
        self.os_edit_var = tk.StringVar(master=self.root)
        self.dienst_edit_var = tk.StringVar(master=self.root)
        self.lccu_lid_edit_var = tk.StringVar(master=self.root)
        self.datum_in_behandeling_edit_var = tk.StringVar(master=self.root)
        self.datum_in_behandeling_checkbox_var = tk.BooleanVar(master=self.root)
        self.soort_bijstand_edit_var = tk.StringVar(master=self.root)
        self.start_bijstand_edit_var = tk.StringVar(master=self.root)
        self.einde_bijstand_edit_var = tk.StringVar(master=self.root)

        # Popup variabelen
        self.popup_window: tk.Toplevel | None = None
        self.soort_bijstand_var = tk.StringVar(master=self.root)
        self.aantal_medewerkers_var = tk.StringVar(master=self.root)
        self.start_bijstand_var = tk.StringVar(master=self.root)
        self.einde_bijstand_var = tk.StringVar(master=self.root)
        self.medewerker_widgets: list[ttk.Combobox] = []
        self._medewerkers_trace_id: str | None = None


class LCCUDatabaseApp:
    def __init__(self, state: GUIState | None = None):
        self.state = state or GUIState()
        self.root = self.state.root
        self.root.title("LCCU Database versie 1.1.1")
        self.root.geometry("700x500")
        icon_path = resource_path("logo_lccu_DB.ico")
        try:
            self.root.iconbitmap(icon_path)
        except Exception:
            # In headless of niet-Windows omgevingen kan dit falen.
            pass

        self.state.notebook.pack(expand=True, fill="both")

        self._current_record_id: str | None = None

        self._build_ingave_tab()
        self._build_zoeken_tab()
        self._build_bewerken_tab()

    # ====================
    # Tabblad: INGAVE
    # ====================
    def _build_ingave_tab(self):
        self.ingave_frame = ttk.Frame(self.state.notebook)
        self.state.notebook.add(self.ingave_frame, text="Ingave")

        self.state.sin_var.trace_add("write", self._update_sin)
        self.state.type_var.trace_add(
            "write", lambda *args: self._update_picklists_ingave()
        )

        tk.Label(self.ingave_frame, text="SIN-nummer").grid(
            row=0, column=0, padx=10, pady=5, sticky="w"
        )
        tk.Entry(self.ingave_frame, textvariable=self.state.sin_var).grid(
            row=0, column=1, padx=10, pady=5, sticky="w"
        )

        tk.Label(self.ingave_frame, text="Type").grid(
            row=1, column=0, padx=10, pady=5, sticky="w"
        )
        type_frame_ingave = tk.Frame(self.ingave_frame)
        type_frame_ingave.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        for opt in ["Mobile", "Computer", "Bijstand"]:
            tk.Radiobutton(
                type_frame_ingave,
                text=opt,
                variable=self.state.type_var,
                value=opt,
                command=self._update_picklists_ingave,
            ).pack(side="left", padx=5)

        tk.Label(self.ingave_frame, text="Subcategorie").grid(
            row=2, column=0, padx=10, pady=5, sticky="w"
        )
        self.subcategorie_dropdown_ingave = ttk.Combobox(
            self.ingave_frame, textvariable=self.state.subcategorie_var
        )
        self.subcategorie_dropdown_ingave.grid(
            row=2, column=1, padx=10, pady=5, sticky="w"
        )

        tk.Label(self.ingave_frame, text="Merk").grid(
            row=3, column=0, padx=10, pady=5, sticky="w"
        )
        tk.Entry(self.ingave_frame, textvariable=self.state.merk_var).grid(
            row=3, column=1, padx=10, pady=5, sticky="w"
        )

        tk.Label(self.ingave_frame, text="Besturingssysteem").grid(
            row=4, column=0, padx=10, pady=5, sticky="w"
        )
        self.os_dropdown_ingave = ttk.Combobox(
            self.ingave_frame, textvariable=self.state.os_var
        )
        self.os_dropdown_ingave.grid(
            row=4, column=1, padx=10, pady=5, sticky="w"
        )

        tk.Label(self.ingave_frame, text="Dienst").grid(
            row=5, column=0, padx=10, pady=5, sticky="w"
        )
        ttk.Combobox(
            self.ingave_frame,
            textvariable=self.state.dienst_var,
            values=diensten,
            state="readonly",
        ).grid(row=5, column=1, padx=10, pady=5, sticky="w")

        tk.Button(
            self.ingave_frame, text="Opslaan", command=self._save_ingave_data
        ).grid(row=6, column=1, pady=10, sticky="w")
        tk.Button(
            self.ingave_frame, text="Reset", command=self._reset_ingave_fields
        ).grid(row=6, column=2, pady=10, sticky="w")

        self._update_picklists_ingave()

    def _update_sin(self, *args):
        s = self.state.sin_var.get().upper()
        if len(s) > 8:
            s = s[:8]
        if s != self.state.sin_var.get():
            self.state.sin_var.set(s)

    def _update_picklists_ingave(self):
        t = self.state.type_var.get()
        if t == "Mobile":
            self.subcategorie_dropdown_ingave["values"] = [
                "GSM",
                "Tablet",
                "Sim",
                "SD-kaart",
                "USB-drive",
                "Andere",
            ]
            self.os_dropdown_ingave["values"] = [
                "Android",
                "GrapheneOS",
                "iOS",
                "Andere",
            ]
        elif t == "Computer":
            self.subcategorie_dropdown_ingave["values"] = [
                "Laptop",
                "Desktop",
                "Losse HD",
                "Andere",
            ]
            self.os_dropdown_ingave["values"] = [
                "Windows",
                "Linux",
                "MacOS",
                "Chromebook",
                "Andere",
            ]
        elif t == "Bijstand":
            self.open_bijstand_popup()
        else:
            self.subcategorie_dropdown_ingave["values"] = []
            self.os_dropdown_ingave["values"] = []
        self.state.subcategorie_var.set("")
        self.state.os_var.set("")

    def _reset_ingave_fields(self):
        self.state.sin_var.set("")
        self.state.type_var.set("Mobile")
        self.state.subcategorie_var.set("")
        self.state.merk_var.set("")
        self.state.os_var.set("")
        self.state.dienst_var.set("")

    def _save_ingave_data(self):
        sin = self.state.sin_var.get().strip()
        t = self.state.type_var.get()
        if t == "Bijstand":
            messagebox.showinfo(
                "Informatie", "Gebruik de popup voor bijstandgegevens."
            )
            return
        subcat = self.state.subcategorie_var.get()
        merk = self.state.merk_var.get()
        os_val = self.state.os_var.get()
        dienst = self.state.dienst_var.get()
        datum_ingave = self.current_iso_timestamp()
        unique_id = None
        if sin != "BIJSTAND":
            if len(sin) != 8 or not (sin[:4].isalpha() and sin[4:].isdigit()):
                messagebox.showerror(
                    "Fout", "SIN moet exact 4 letters en 4 cijfers bevatten!"
                )
                return
            sin = sin[:4].upper() + sin[4:]
        try:
            with connect_db() as conn:
                cursor = conn.cursor()
                cursor.execute(
                """
                INSERT INTO objecten (sin, type, subcategorie, merk, os, dienst, datum_ingave, unique_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (sin, t, subcat, merk, os_val, dienst, datum_ingave, unique_id),
                )
            messagebox.showinfo("Succes", "Gegevens succesvol opgeslagen!")
            self._reset_ingave_fields()
        except sqlite3.Error as e:
            print(f"Databasefout bij opslaan: {e}")
            messagebox.showerror(
                "Databasefout", f"Fout bij het opslaan: {str(e)}"
            )

    # --- Bijstand-popup functies voor Ingave ---
    def save_data_from_popup(self):
        soort_bijstand = self.state.soort_bijstand_var.get()
        medewerkers_list = [w.get() for w in self.state.medewerker_widgets]
        start_input = self.state.start_bijstand_var.get()
        einde_input = self.state.einde_bijstand_var.get()
        try:
            start_dt = (
                self.parse_dutch_datetime(start_input)
                if start_input and start_input.strip()
                else None
            )
            einde_dt = (
                self.parse_dutch_datetime(einde_input)
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

        start_bijstand = self.datetime_to_iso(start_dt) if start_dt else None
        einde_bijstand = self.datetime_to_iso(einde_dt) if einde_dt else None
        try:
            datum_ingave = self.current_iso_timestamp()
            object_id = insert_bijstand_record(
                soort_bijstand=soort_bijstand,
                dienst=self.state.dienst_var.get(),
                medewerkers=medewerkers_list,
                start_bijstand=start_bijstand,
                einde_bijstand=einde_bijstand,
                datum_ingave=datum_ingave,
            )
            messagebox.showinfo("Succes", "Bijstand succesvol opgeslagen!")
            self.close_popup()
        except sqlite3.Error as e:
            print(f"Databasefout bij opslaan bijstand: {e}")
            messagebox.showerror(
                "Databasefout",
                f"Fout bij het opslaan in de database: {str(e)}",
            )

    def open_bijstand_popup(self):
        if self.state.popup_window is not None and self.state.popup_window.winfo_exists():
            self.state.popup_window.destroy()
        self.state.popup_window = tk.Toplevel(self.root)
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

        tk.Label(self.state.popup_window, text="Aantal medewerkers LCCU").pack(
            pady=5
        )
        tk.Entry(
            self.state.popup_window, textvariable=self.state.aantal_medewerkers_var
        ).pack(pady=5)

        medewerkers_frame = tk.Frame(self.state.popup_window)
        medewerkers_frame.pack(pady=5)

        def update_medewerkers(*args):
            if not medewerkers_frame.winfo_exists():
                return
            for widget in medewerkers_frame.winfo_children():
                widget.destroy()
            try:
                value = self.state.aantal_medewerkers_var.get()
                aantal_medewerkers = int(value.strip()) if value.strip().isdigit() else 0
            except ValueError:
                aantal_medewerkers = 0
            self.state.medewerker_widgets.clear()
            for i in range(aantal_medewerkers):
                tk.Label(medewerkers_frame, text=f"Medewerker {i + 1}").grid(
                    row=i, column=0, padx=5, pady=2
                )
                medewerker_combobox = ttk.Combobox(
                    medewerkers_frame, values=medewerkers
                )
                medewerker_combobox.grid(row=i, column=1, padx=5, pady=2)
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
            values=diensten,
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

        def validate_dates():
            self.save_data_from_popup()

        tk.Button(
            self.state.popup_window, text="Opslaan", command=validate_dates
        ).pack(pady=10)
        self.state.popup_window.protocol("WM_DELETE_WINDOW", self.close_popup)

    def close_popup(self):
        if self.state.popup_window:
            self.state.popup_window.destroy()
            self.state.popup_window = None

    # ====================
    # Tabblad: ZOEKEN
    # ====================
    def _build_zoeken_tab(self):
        self.zoeken_frame = ttk.Frame(self.state.notebook)
        self.state.notebook.add(self.zoeken_frame, text="Zoeken")

        tk.Label(self.zoeken_frame, text="Zoek op SIN").grid(
            row=0, column=0, padx=10, pady=5, sticky="w"
        )
        tk.Entry(
            self.zoeken_frame, textvariable=self.state.sin_zoek_var
        ).grid(row=0, column=1, padx=10, pady=5, sticky="w")

        tk.Label(self.zoeken_frame, text="Datum van (dd-mm-jjjj)").grid(
            row=1, column=0, padx=10, pady=5, sticky="w"
        )
        tk.Entry(
            self.zoeken_frame, textvariable=self.state.datum_vanaf_var
        ).grid(row=1, column=1, padx=10, pady=5, sticky="w")

        tk.Label(self.zoeken_frame, text="Datum tot (dd-mm-jjjj)").grid(
            row=2, column=0, padx=10, pady=5, sticky="w"
        )
        tk.Entry(
            self.zoeken_frame, textvariable=self.state.datum_tot_var
        ).grid(row=2, column=1, padx=10, pady=5, sticky="w")

        tk.Checkbutton(
            self.zoeken_frame,
            text="Doorzoek datum_ingave",
            variable=self.state.include_datum_ingave_var,
        ).grid(row=3, column=0, padx=10, pady=5, sticky="w")

        tk.Button(
            self.zoeken_frame, text="Zoeken", command=self.zoek_objecten
        ).grid(row=3, column=1, padx=10, pady=5, sticky="w")
        tk.Button(
            self.zoeken_frame, text="Reset", command=self.reset_zoekvelden
        ).grid(row=3, column=2, padx=10, pady=5, sticky="w")

        self.tree_frame_zoek = tk.Frame(self.zoeken_frame)
        self.tree_frame_zoek.grid(
            row=4, column=0, columnspan=3, padx=10, pady=10, sticky="nsew"
        )
        self.tree_scroll_y_zoek = ttk.Scrollbar(
            self.tree_frame_zoek, orient="vertical"
        )
        self.tree_scroll_y_zoek.grid(row=0, column=1, sticky="ns")
        self.tree_scroll_x_zoek = ttk.Scrollbar(
            self.tree_frame_zoek, orient="horizontal"
        )
        self.tree_scroll_x_zoek.grid(row=1, column=0, sticky="ew")
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
            self.tree_frame_zoek,
            columns=columns,
            show="headings",
            displaycolumns=columns[1:],
            yscrollcommand=self.tree_scroll_y_zoek.set,
            xscrollcommand=self.tree_scroll_x_zoek.set,
        )
        self.result_tree.grid(row=0, column=0, sticky="nsew")
        self.tree_scroll_y_zoek.config(command=self.result_tree.yview)
        self.tree_scroll_x_zoek.config(command=self.result_tree.xview)
        for col in columns:
            self.result_tree.heading(col, text=col)
        self.zoeken_frame.grid_rowconfigure(4, weight=1)
        self.zoeken_frame.grid_columnconfigure(0, weight=1)
        self.tree_frame_zoek.grid_rowconfigure(0, weight=1)
        self.tree_frame_zoek.grid_columnconfigure(0, weight=1)

    @staticmethod
    def parse_dutch_datetime(value: str) -> datetime:
        if value is None:
            raise ValueError("Datumwaarde ontbreekt")
        value = value.strip()
        if not value:
            raise ValueError("Datumwaarde ontbreekt")
        return datetime.strptime(value, "%d-%m-%Y %H:%M")

    @staticmethod
    def datetime_to_iso(dt: datetime) -> str:
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    @classmethod
    def parse_dutch_to_iso(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value:
            return None
        dt = cls.parse_dutch_datetime(value)
        return cls.datetime_to_iso(dt)

    @staticmethod
    def current_iso_timestamp() -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def format_iso_to_dutch(date_str):
        if not date_str:
            return ""
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            return dt.strftime("%d-%m-%Y %H:%M")
        except Exception:
            return date_str

    @classmethod
    def format_datetime_for_display(cls, value: str | None) -> str:
        return cls.format_iso_to_dutch(value) if value else ""

    @staticmethod
    def format_date(date_str):
        try:
            return datetime.strptime(date_str.strip(), "%d-%m-%Y").strftime(
                "%Y-%m-%d"
            )
        except ValueError:
            return None

    @staticmethod
    def auto_adjust_column_width(tree, tree_frame, tree_scroll_x):
        tree.update_idletasks()
        default_font = tkFont.nametofont("TkDefaultFont")
        total_width = 0
        columns = tree["columns"]
        for col_index, col in enumerate(columns):
            header_width = default_font.measure(col) + 10
            max_width = header_width
            for row in tree.get_children():
                vals = tree.item(row, "values")
                if col_index < len(vals):
                    cell_width = default_font.measure(str(vals[col_index])) + 10
                    max_width = max(max_width, cell_width)
            tree.column(col, width=max_width, stretch=False)
            total_width += max_width
        tree_frame.update_idletasks()
        frame_width = tree_frame.winfo_width()
        if total_width > frame_width:
            tree_scroll_x.grid(row=1, column=0, sticky="ew")
            tree.configure(xscrollcommand=tree_scroll_x.set)
        else:
            tree_scroll_x.grid_remove()

    def zoek_objecten(self):
        sin = self.state.sin_zoek_var.get()
        datum_vanaf = self.format_date(self.state.datum_vanaf_var.get())
        datum_tot = self.format_date(self.state.datum_tot_var.get())
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
            with connect_db() as conn:
                cursor = conn.cursor()
                cursor.execute(query, tuple(params))
                results = cursor.fetchall()
            for row in self.result_tree.get_children():
                self.result_tree.delete(row)
            for row in results:
                row = list(row)
                for index in (8, 9, 10):
                    row[index] = self.format_datetime_for_display(row[index])
                self.result_tree.insert("", "end", values=row)
            self.root.after(
                100,
                lambda: self.auto_adjust_column_width(
                    self.result_tree, self.tree_frame_zoek, self.tree_scroll_x_zoek
                ),
            )
        except sqlite3.Error as e:
            print(f"Databasefout bij zoeken: {e}")
            messagebox.showerror(
                "Databasefout", f"Fout bij het zoeken: {str(e)}"
            )

    def reset_zoekvelden(self):
        self.state.sin_zoek_var.set("")
        self.state.datum_vanaf_var.set("")
        self.state.datum_tot_var.set("")
        for row in self.result_tree.get_children():
            self.result_tree.delete(row)

    # ====================
    # Tabblad: BEWERKEN
    # ====================
    def _build_bewerken_tab(self):
        self.bewerken_frame = ttk.Frame(self.state.notebook)
        self.state.notebook.add(self.bewerken_frame, text="Bewerken")

        self.state.type_edit_var.trace_add(
            "write", lambda *args: self._update_dropdowns_bewerken()
        )

        tk.Label(self.bewerken_frame, text="SIN-nummer").grid(
            row=0, column=0, padx=10, pady=5, sticky="w"
        )
        tk.Entry(
            self.bewerken_frame, textvariable=self.state.sin_edit_var
        ).grid(row=0, column=1, padx=10, pady=5, sticky="w")

        tk.Label(self.bewerken_frame, text="Type").grid(
            row=1, column=0, padx=10, pady=5, sticky="w"
        )
        type_frame_bewerken = tk.Frame(self.bewerken_frame)
        type_frame_bewerken.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        for opt in ["Mobile", "Computer", "Bijstand"]:
            tk.Radiobutton(
                type_frame_bewerken,
                text=opt,
                variable=self.state.type_edit_var,
                value=opt,
            ).pack(side="left", padx=5)

        tk.Label(self.bewerken_frame, text="Subcategorie").grid(
            row=2, column=0, padx=10, pady=5, sticky="w"
        )
        self.subcategorie_dropdown_bewerken = ttk.Combobox(
            self.bewerken_frame, textvariable=self.state.subcategorie_edit_var
        )
        self.subcategorie_dropdown_bewerken.grid(
            row=2, column=1, padx=10, pady=5, sticky="w"
        )

        tk.Label(self.bewerken_frame, text="Merk").grid(
            row=3, column=0, padx=10, pady=5, sticky="w"
        )
        tk.Entry(
            self.bewerken_frame, textvariable=self.state.merk_edit_var
        ).grid(row=3, column=1, padx=10, pady=5, sticky="w")

        tk.Label(self.bewerken_frame, text="Besturingssysteem").grid(
            row=4, column=0, padx=10, pady=5, sticky="w"
        )
        self.os_dropdown_bewerken = ttk.Combobox(
            self.bewerken_frame, textvariable=self.state.os_edit_var
        )
        self.os_dropdown_bewerken.grid(
            row=4, column=1, padx=10, pady=5, sticky="w"
        )

        tk.Label(self.bewerken_frame, text="Dienst").grid(
            row=5, column=0, padx=10, pady=5, sticky="w"
        )
        ttk.Combobox(
            self.bewerken_frame,
            textvariable=self.state.dienst_edit_var,
            values=diensten,
            state="readonly",
        ).grid(row=5, column=1, padx=10, pady=5, sticky="w")

        tk.Label(self.bewerken_frame, text="Soort bijstand").grid(
            row=6, column=0, padx=10, pady=5, sticky="w"
        )
        tk.Entry(
            self.bewerken_frame, textvariable=self.state.soort_bijstand_edit_var
        ).grid(row=6, column=1, padx=10, pady=5, sticky="w")

        tk.Label(self.bewerken_frame, text="LCCU lid in behandeling").grid(
            row=7, column=0, padx=10, pady=5, sticky="w"
        )
        ttk.Combobox(
            self.bewerken_frame,
            textvariable=self.state.lccu_lid_edit_var,
            values=medewerkers,
        ).grid(row=7, column=1, padx=10, pady=5, sticky="w")

        tk.Label(
            self.bewerken_frame, text="Start bijstand (dd-mm-jjjj uu:mm)"
        ).grid(row=8, column=0, padx=10, pady=5, sticky="w")
        tk.Entry(
            self.bewerken_frame, textvariable=self.state.start_bijstand_edit_var
        ).grid(row=8, column=1, padx=10, pady=5, sticky="w")

        tk.Label(
            self.bewerken_frame, text="Einde bijstand (dd-mm-jjjj uu:mm)"
        ).grid(row=9, column=0, padx=10, pady=5, sticky="w")
        tk.Entry(
            self.bewerken_frame, textvariable=self.state.einde_bijstand_edit_var
        ).grid(row=9, column=1, padx=10, pady=5, sticky="w")

        tk.Label(self.bewerken_frame, text="Datum in behandeling").grid(
            row=10, column=0, padx=10, pady=5, sticky="w"
        )
        self.datum_in_behandeling_entry = tk.Entry(
            self.bewerken_frame,
            textvariable=self.state.datum_in_behandeling_edit_var,
            state="disabled",
        )
        self.datum_in_behandeling_entry.grid(
            row=10, column=1, padx=10, pady=5, sticky="w"
        )
        tk.Checkbutton(
            self.bewerken_frame,
            text="Datum in behandeling invullen",
            variable=self.state.datum_in_behandeling_checkbox_var,
            command=self._toggle_datum_in_behandeling,
        ).grid(row=10, column=2, padx=10, pady=5)

        tk.Button(
            self.bewerken_frame, text="Opslaan", command=self.update_record
        ).grid(row=11, column=1, pady=10)

        self.result_tree.bind("<Double-1>", self.load_record_for_edit)

    def _update_dropdowns_bewerken(self):
        t = self.state.type_edit_var.get()
        if t == "Mobile":
            self.subcategorie_dropdown_bewerken["values"] = [
                "GSM",
                "Tablet",
                "Sim",
                "SD-kaart",
                "USB-drive",
                "Andere",
            ]
            self.os_dropdown_bewerken["values"] = [
                "Android",
                "GrapheneOS",
                "iOS",
                "Andere",
            ]
        elif t == "Computer":
            self.subcategorie_dropdown_bewerken["values"] = [
                "Laptop",
                "Desktop",
                "Losse HD",
                "Andere",
            ]
            self.os_dropdown_bewerken["values"] = [
                "Windows",
                "Linux",
                "MacOS",
                "Chromebook",
                "Andere",
            ]
        else:
            self.subcategorie_dropdown_bewerken["values"] = []
            self.os_dropdown_bewerken["values"] = []

    def _toggle_datum_in_behandeling(self):
        if self.state.datum_in_behandeling_checkbox_var.get():
            self.state.datum_in_behandeling_edit_var.set(
                datetime.now().strftime("%d-%m-%Y %H:%M")
            )
        else:
            self.state.datum_in_behandeling_edit_var.set("")

    def update_record(self):
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
                self.parse_dutch_datetime(start_input)
                if start_input
                else None
            )
            einde_dt = (
                self.parse_dutch_datetime(einde_input)
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
                datum_in_behandeling_iso = self.parse_dutch_to_iso(
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
            self.datetime_to_iso(start_dt) if start_dt else None
        )
        einde_bijstand_iso = (
            self.datetime_to_iso(einde_dt) if einde_dt else None
        )
        is_bijstand_record = (
            self.state.type_edit_var.get().strip().lower() == "bijstand"
            or self.state.sin_edit_var.get().strip().upper() == "BIJSTAND"
        )
        try:
            with connect_db() as conn:
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
                    self.state.sin_edit_var.get(),
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
            success_message = "Record bijgewerkt!"
            if is_bijstand_record:
                success_message += (
                    "\n\nTODO: Aanpassen van de medewerkerslijst is nog niet "
                    "beschikbaar in dit scherm. Bijstandoverzichten blijven "
                    "wel gesynchroniseerd met de aangepaste start- en eindtijden."
                )
            messagebox.showinfo("Succes", success_message)
            self.zoek_objecten()
        except sqlite3.Error as e:
            print(f"Databasefout bij bijwerken: {e}")
            messagebox.showerror(
                "Databasefout", f"Fout bij het bijwerken: {str(e)}"
            )

    def load_record_for_edit(self, event):
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
                with connect_db() as conn:
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
            self.state.soort_bijstand_edit_var.set(soort_bijstand_value)
        else:
            self.state.soort_bijstand_edit_var.set("")
        has_datum_in_behandeling = bool(values[8])
        self.state.datum_in_behandeling_edit_var.set(
            self.format_datetime_for_display(values[8])
        )
        self.state.start_bijstand_edit_var.set(
            self.format_datetime_for_display(values[9])
        )
        self.state.einde_bijstand_edit_var.set(
            self.format_datetime_for_display(values[10])
        )
        self.state.datum_in_behandeling_checkbox_var.set(has_datum_in_behandeling)
        self.state.notebook.select(self.bewerken_frame)

    def run(self):
        self.root.mainloop()


def main():
    check_or_create_database()
    app = LCCUDatabaseApp()
    app.run()


if __name__ == "__main__":
    main()
