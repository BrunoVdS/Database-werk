# Deel 2 – Gebruik

## Opstarten
1. Controleer of het databasepad bereikbaar is.
2. Start de applicatie met `python "LCCU Database.py"`.
3. Het hoofdvenster toont de tabbladen **Ingave**, **Zoeken** en **Bewerken**.

## Ingave
1. Vul het SIN in (vier letters + vier cijfers of `BIJSTAND`).
2. Kies een type. Bij type “Bijstand” wordt de bijstand-popup automatisch geopend.
3. Selecteer subcategorie, merk, OS en dienst.
4. Vul eventuele extra velden in en klik op **Opslaan**.

## Bijstand-popup
- Kies soort bijstand, dienst en vul start/einddatum in.
- Selecteer het aantal medewerkers. Het venster toont evenveel naamvelden als opgegeven aantal.
- Datums worden gevalideerd op formaat en chronologie.
- Klik op **Opslaan** om zowel het object als de medewerkers vast te leggen.

## Zoeken
1. Gebruik filters op SIN, datum of beide.
2. Klik op **Zoeken**; resultaten verschijnen in een tabel.
3. Dubbelklik op een resultaat om details te bekijken of over te gaan naar **Bewerken**.
4. **Reset** wist alle filters en resultaten.

## Bewerken
1. Selecteer een record via het **Zoeken**-tabblad.
2. De velden worden ingevuld; pas gewenste waarden aan.
3. Controleer datums en SIN op geldigheid.
4. Klik op **Opslaan** om wijzigingen door te voeren.
5. Bij bijstandsrecords worden gekoppelde medewerkers geactualiseerd op basis van de invoer.

## Meldingen en foutafhandeling
- Ongeldige SIN of datums genereren directe foutmeldingen.
- Succesvolle bewerkingen tonen een bevestiging.
