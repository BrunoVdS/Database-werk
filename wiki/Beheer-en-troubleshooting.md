# Beheer en troubleshooting

## Veelvoorkomende problemen

### Databasepad niet gevonden
- Controleer of `LCCU_DB_PATH` correct staat ingesteld.
- Verifieer `config.ini` of `config.json` op een geldige `database.path`-waarde.
- Controleer netwerktoegang tot het UNC-pad.

### Foutmelding bij datumvelden
- Zorg dat datums het formaat `dd-mm-jjjj` hebben in de UI.
- Controleer of de einddatum niet voor de startdatum ligt.
- Bekijk logica in `parse_date` en `format_date` voor conversieproblemen.

### SIN-validatie faalt
- Gebruik vier hoofdletters gevolgd door vier cijfers (bijvoorbeeld `ABCD1234`).
- Voor bijstandsrecords mag `BIJSTAND` gebruikt worden.

### Bijstand-medewerkers ontbreken
- Controleer of het aantal geselecteerde medewerkers overeenkomt met de ingevulde namen.
- De tabel `medewerkers_bijstand` wordt opgeschoond en opnieuw gevuld bij elke opslag.

## Onderhoud
- Maak periodiek back-ups van de SQLite-database.
- Documenteer wijzigingen in de lijst van diensten in `LCCU Database.py`.
- Houd dependencies up-to-date en test bij upgrades van Python of Tkinter.

## Logging
Momenteel is er geen uitgebreide logging ingebouwd. Overweeg bij productiegebruik het toevoegen van logging via het `logging`-pakket of het schrijven van audit-entries in een aparte tabel.
