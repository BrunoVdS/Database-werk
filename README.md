# Database-werk

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

---

## Manual Regression Checklist

Invalid SIN edit is rejected

Start de applicatie en open het tabblad Bewerken.
Selecteer een bestaand record met een geldig SIN (bijvoorbeeld ABCD1234).
Pas het SIN-veld aan naar een ongeldig formaat, zoals A1C3.
Klik op Bijwerken en bevestig dat een foutvenster verschijnt met de melding dat het SIN exact vier letters en vier cijfers moet bevatten.
Sluit het dialoogvenster, laad het record opnieuw en controleer dat het oorspronkelijke SIN ongewijzigd is gebleven in de database.
terug op het standaardpad. Hierdoor kan eenvoudig worden geschakeld tussen de
productiedatabase en een lokale ontwikkeldatabase zonder de code aan te passen.
