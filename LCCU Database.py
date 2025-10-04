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
from views.bewerken import BewerkenTab
from views.bijstand_popup import BijstandPopup
from views.ingave import IngaveTab
from views.zoeken import ZoekenTab


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


def _validate_sin(value: str) -> str:
    sin = value.strip()
    if sin.upper() == "BIJSTAND":
        return "BIJSTAND"
    if len(sin) != 8 or not (sin[:4].isalpha() and sin[4:].isdigit()):
        raise ValueError("SIN moet exact 4 letters en 4 cijfers bevatten!")
    return sin[:4].upper() + sin[4:]


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


def parse_dutch_datetime(value: str) -> datetime:
    if value is None:
        raise ValueError("Datumwaarde ontbreekt")
    value = value.strip()
    if not value:
        raise ValueError("Datumwaarde ontbreekt")
    return datetime.strptime(value, "%d-%m-%Y %H:%M")


def datetime_to_iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def parse_dutch_to_iso(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    if not value:
        return None
    dt = parse_dutch_datetime(value)
    return datetime_to_iso(dt)


def current_iso_timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def format_iso_to_dutch(date_str: str | None) -> str:
    if not date_str:
        return ""
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%d-%m-%Y %H:%M")
    except Exception:
        return date_str or ""


def format_datetime_for_display(value: str | None) -> str:
    return format_iso_to_dutch(value) if value else ""


def format_date(date_str: str) -> str | None:
    try:
        return datetime.strptime(date_str.strip(), "%d-%m-%Y").strftime(
            "%Y-%m-%d"
        )
    except ValueError:
        return None


def auto_adjust_column_width(
    tree: ttk.Treeview, tree_frame: tk.Frame, tree_scroll_x: ttk.Scrollbar
) -> None:
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


class MainWindow:
    def __init__(self, state: GUIState | None = None):
        self.state = state or GUIState()
        self.root = self.state.root
        self.root.title("LCCU Database versie 1.1.1")
        self.root.geometry("700x500")
        icon_path = resource_path("logo_lccu_DB.ico")
        try:
            self.root.iconbitmap(icon_path)
        except Exception:
            pass

        self.state.notebook.pack(expand=True, fill="both")

        self.bijstand_popup = BijstandPopup(
            state=self.state,
            medewerkers=medewerkers,
            diensten=diensten,
            parse_dutch_datetime=parse_dutch_datetime,
            datetime_to_iso=datetime_to_iso,
            current_timestamp=current_iso_timestamp,
            insert_bijstand_record=insert_bijstand_record,
        )

        self.ingave_tab = IngaveTab(
            state=self.state,
            diensten=diensten,
            validate_sin=_validate_sin,
            connect_db=connect_db,
            current_timestamp=current_iso_timestamp,
            popup=self.bijstand_popup,
        )

        self.zoeken_tab = ZoekenTab(
            state=self.state,
            connect_db=connect_db,
            format_date=format_date,
            format_datetime_for_display=format_datetime_for_display,
            auto_adjust_column_width=auto_adjust_column_width,
        )

        self.bewerken_tab = BewerkenTab(
            state=self.state,
            connect_db=connect_db,
            validate_sin=_validate_sin,
            parse_dutch_datetime=parse_dutch_datetime,
            parse_dutch_to_iso=parse_dutch_to_iso,
            datetime_to_iso=datetime_to_iso,
            format_datetime_for_display=format_datetime_for_display,
            search_callback=self.zoeken_tab.zoek_objecten,
            result_tree=self.zoeken_tab.result_tree,
        )

    def run(self) -> None:
        self.root.mainloop()


LCCUDatabaseApp = MainWindow



def main():
    check_or_create_database()
    app = LCCUDatabaseApp()
    app.run()


if __name__ == "__main__":
    main()
