# Handleiding LCCU Database Applicatie

## Voorbladvoorstel
- **Titel:** LCCU Database Applicatie – Handleiding
- **Versie:** 1.0
- **Datum:** $(date +%d-%m-%Y)
- Voeg een illustratie toe van het architectuuroverzicht (zie Mermaid-diagram hieronder).

## Inhoudsopgave
1. Deel 1 – De code
2. Deel 2 – Werking van het programma
3. Bijlagen

---

## Deel 1 – De code

### Architectuur in vogelvlucht
Het startpunt is de functie `main()` in `LCCU Database.py`. Deze functie zorgt dat de SQLite-tabellen bestaan en start daarna het Tkinter-hoofdvenster (`LCCUDatabaseApp`). De databaseverbindingen verlopen via `connect_db()` dat het pad ophaalt uit de configuratie.

```mermaid
graph TD
    A[main()] --> B[check_or_create_database()]
    B --> B1[create_table()]
    B --> B2[create_medewerkers_bijstand_table()]
    B --> B3[normalize_datetime_fields()]
    A --> C[LCCUDatabaseApp/MainWindow]
    C --> D[IngaveTab]
    C --> E[ZoekenTab]
    C --> F[BewerkenTab]
    C --> G[BijstandPopup]
    subgraph Configuratie
        H[config.get_database_path()]
    end
    D -->|Schrijft records| I[(SQLite: objecten)]
    G -->|Voegt bijstand toe| I
    F -->|Past records aan| I
    G -->|Logt medewerkers| J[(SQLite: medewerkers_bijstand)]
```

### Componentoverzicht
| Module | Rol |
| --- | --- |
| `config.py` | Bepaalt het databasepad via omgevingsvariabelen, INI- en JSON-bestanden en valt terug op een UNC-standaardpad. |
| `LCCU Database.py` | Centrale applicatielogica: database-initialisatie, datumhelpers, lijsten met diensten/medewerkers, Tkinter-hoofdscherm en bijstandsinvoer. |
| `views/ingave.py` | Tabblad “Ingave” voor het registreren van objecten, inclusief SIN-validatie en specifieke comboboxen per type. |
| `views/zoeken.py` | Tabblad “Zoeken” met filters op SIN en datums en weergave in een `Treeview`. |
| `views/bewerken.py` | Tabblad “Bewerken” met dubbele-klikselectie, datumvalidatie en updates van bijstand- en medewerkersgegevens. |
| `views/bijstand_popup.py` | Popup voor het registreren van bijstandsdossiers, met dynamische medewerkersvelden en datumcontroles. |

### Databaselaag
- Tabel `objecten` bevat de kerngegevens (SIN, type, subcategorie, merk, OS, dienst, datums, enz.).
- Tabel `medewerkers_bijstand` houdt medewerkers per bijstandsrecord bij met een foreign key naar `objecten`.
- Bij het opstarten worden bestaande datumvelden genormaliseerd naar ISO-formaat zodat vergelijkingen en queries betrouwbaar zijn.

### Hulpfuncties en validaties
- `insert_bijstand_record` schrijft het hoofddossier en de gekoppelde medewerkers weg en vult ontbrekende waarden (datum, uniek nummer) aan.
- `_validate_sin` accepteert enkel vier letters gevolgd door vier cijfers of het sleutelwoord `BIJSTAND`.
- Datumhelpers converteren tussen Nederlands formaat en ISO-stempels voor opslag en presentatie.

### GUIState en MainWindow
- `GUIState` bundelt alle `StringVar`- en `BooleanVar`-instanties zodat tabbladen dezelfde data delen.
- `MainWindow` configureert het venster (titel, icoon, grootte) en registreert de drie tabbladen plus de bijstand-popup.
- De lijst met mogelijke diensten wordt gedeeld tussen de verschillende schermen.

---

## Deel 2 – Werking van het programma

### Opstarten
1. Zorg dat de gewenste SQLite-locatie beschikbaar is (zie Bijlage A).
2. Start het programma; het hoofdvenster bevat drie tabbladen: **Ingave**, **Zoeken** en **Bewerken**.

### Ingave-tabblad
1. Vul het SIN-nummer in; het veld forceert hoofdletters en maximaal acht tekens.
2. Kies het type (Mobile, Computer of Bijstand). Bij “Bijstand” opent automatisch de popup voor extra gegevens.
3. Selecteer subcategorie, merk, besturingssysteem en dienst (diensten komen uit de vaste lijst).
4. Klik op **Opslaan**; bij een fout in het SIN verschijnt een melding, anders worden de gegevens opgeslagen.

### Bijstand-popup
- De popup vraagt soort bijstand, aantal medewerkers, dienst en start-/einddatum. Het aantal medewerkers bepaalt dynamisch hoeveel naamvelden zichtbaar zijn.
- Datums worden gevalideerd op formaat en chronologie; bij fouten verschijnt een melding.
- Opslaan schrijft zowel het objectrecord als de medewerkers naar de database.

### Zoeken-tabblad
1. Filter optioneel op (deel van) een SIN of op een datumvenster; je kunt kiezen om ook `datum_ingave` mee te nemen.
2. Resultaten verschijnen in een tabel; datums worden getoond in leesbaar Nederlands formaat en kolommen schalen automatisch.
3. **Reset** wist filters en resultaten.

### Bewerken-tabblad
1. Dubbelklik in het zoekresultaat om een record te laden; de tab schakelt automatisch naar **Bewerken** en vult alle velden in, inclusief bijstandsgegevens.
2. Aangepaste datums worden gecontroleerd op formaat en logische volgorde.
3. SIN’s worden opnieuw gevalideerd voordat wijzigingen worden opgeslagen.
4. Bij bijstand-records worden gekoppelde medewerkers opnieuw opgeslagen en het aantal wordt bijgewerkt.
5. Bij succes verschijnt een bevestiging en worden de zoekresultaten ververst.

---

## Bijlage A – Configuratie en beheer
- Stel de omgevingsvariabele `LCCU_DB_PATH` in voor een alternatief databasepad.
- Of gebruik `config.ini`/`config.json` met een `database.path`-sleutel; bij afwezigheid wordt het UNC-standaardpad gebruikt.
- Alle verbindingen gebruiken `sqlite3` en worden netjes gesloten via context managers of expliciete afsluiting.

## Bijlage B – Validaties en foutafhandeling
- Datumwaarden worden genormaliseerd bij opstart en bij elke invoer; ongeldige waarden worden geweigerd met duidelijke meldingen.
- Bijstandsinvoer vult automatisch `aantal_medewerkers` op basis van het aantal geselecteerde medewerkers.

---

## PDF Genereren
1. Kopieer (of link) dit document naar `handleiding.md` in een aparte documentatiemap.
2. Voeg optioneel screenshots toe in de relevante secties.
3. Converteer naar PDF met bijvoorbeeld Pandoc:
   ```bash
   pandoc docs/handleiding.md -o handleiding.pdf --from gfm --toc --pdf-engine=xelatex
   ```
4. Controleer in de PDF of het diagram goed wordt gerenderd. Als Mermaid niet wordt ondersteund, render het diagram vooraf en voeg de afbeelding in.
