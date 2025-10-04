# Database-werk

Database LCCU verder uitwerken.

## Databaseconfiguratie

De applicatie gebruikt standaard de historische UNC-locatie op het netwerk:
`\\\\file01.storage\\smB-usr-lrnas\\lr-lccu\\Bruno\\objecten.db`. In
ontwikkelomgevingen kan een andere database worden gekozen via één van de
volgende opties (in aflopende prioriteit):

1. **Omgevingsvariabele** – Stel `LCCU_DB_PATH` in op het gewenste pad voordat u
   de applicatie start.
2. **INI-bestand** – Maak een `config.ini` in dezelfde map als de applicatie (of
   in de huidige werkmap) met bijvoorbeeld:
   ```ini
   [database]
   path = C:/pad/naar/objecten_dev.db
   ```
3. **JSON-bestand** – Maak een `config.json` in dezelfde map als de applicatie
   (of in de huidige werkmap) met bijvoorbeeld:
   ```json
   {
     "database": {
       "path": "C:/pad/naar/objecten_dev.db"
     }
   }
   ```

Wanneer geen van deze opties beschikbaar is, valt de applicatie automatisch
terug op het standaardpad. Hierdoor kan eenvoudig worden geschakeld tussen de
productiedatabase en een lokale ontwikkeldatabase zonder de code aan te passen.
