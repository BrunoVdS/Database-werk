# Database-werk

Database LCCU verder uitwerken

## Databaseconfiguratie

De applicatie gebruikt standaard de netwerkdatabase op het UNC-pad
`\\\\file01.storage\\smB-usr-lrnas\\lr-lccu\\Bruno\\objecten.db`. Wanneer dit pad
niet bereikbaar is, kun je een alternatief pad instellen via één van de
volgende opties (in onderstaande volgorde van prioriteit):

1. **Omgevingsvariabele** – stel `LCCU_DB_PATH` in op het volledige pad naar je
   databasebestand.
2. **INI-configuratie** – maak een `config.ini` (of `settings.ini`) bestand in de
   projectmap met:
   ```ini
   [database]
   path = C:\\pad\\naar\\objecten.db
   ```
3. **JSON-configuratie** – maak een `config.json` (of `settings.json`) bestand in
   de projectmap met bijvoorbeeld:
   ```json
   {
     "database_path": "C:/pad/naar/objecten.db"
   }
   ```
   of
   ```json
   {
     "database": {
       "path": "C:/pad/naar/objecten.db"
     }
   }
   ```

De applicatie controleert eerst de omgevingsvariabele, daarna de aanwezige
configuratiebestanden en valt anders terug op het standaard UNC-pad.

### Lokale ontwikkeling

Voor lokale ontwikkeling kun je eenvoudig een kopie van de database maken en
het pad ernaartoe opgeven met één van de bovenstaande methoden. Bijvoorbeeld:

```bash
set LCCU_DB_PATH=C:\\Users\\<naam>\\Desktop\\objecten_dev.db  # Windows
export LCCU_DB_PATH="/Users/<naam>/objecten_dev.db"              # macOS/Linux
```

Of plaats een `config.ini` in dezelfde map als de applicatie met het pad naar je
lokale database. Zodra de applicatie wordt gestart, toont ze een duidelijke
foutmelding als de opgegeven locatie niet bereikbaar is.
