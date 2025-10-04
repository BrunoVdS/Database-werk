# Installatie en configuratie

## Vereisten
- Python 3.10 of hoger
- `pip` voor het installeren van dependencies
- Toegang tot het gewenste netwerkpad voor de SQLite-database

## Stappenplan
1. **Repository clonen**
   ```bash
   git clone <repository-url>
   cd Database-werk
   ```

2. **Virtuele omgeving aanmaken (optioneel maar aanbevolen)**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
   ```

3. **Dependencies installeren**
   ```bash
   pip install -r requirements.txt
   ```
   > Bestaat er geen `requirements.txt`, installeer dan minimaal `tk` (voor Tkinter) en `python-dotenv` indien configuratie via `.env` wordt gebruikt.

4. **Databasepad configureren**
   - Zet de omgevingsvariabele `LCCU_DB_PATH` naar het gewenste pad; of
   - Vul `config.ini` of `config.json` aan met een `database.path`-sleutel; of
   - Gebruik de standaard UNC-locatie zoals gedefinieerd in `config.py`.

5. **Applicatie starten**
   ```bash
   python "LCCU Database.py"
   ```

## Database-initialisatie
Bij de eerste start maakt het programma automatisch de tabellen `objecten` en `medewerkers_bijstand` aan en normaliseert bestaande datumvelden.

## PDF-handleiding genereren
Volg de stappen in [`docs/handleiding.md`](../docs/handleiding.md) om een PDF-versie van de handleiding te maken met behulp van Pandoc.
