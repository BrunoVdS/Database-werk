# Testen en kwaliteitscontrole

## Handmatige regressietests
| Scenario | Stappen | Verwacht resultaat |
| --- | --- | --- |
| SIN-validatie | Voer `ABCD1234` in, sla op. Probeer `abcd1234` of `12345678`. | Eerste wordt geaccepteerd, andere geven foutmelding. |
| Datumcontrole | Vul startdatum `01-01-2024`, einddatum `31-12-2023`. | Applicatie geeft foutmelding over datumvolgorde. |
| Bijstand-medewerkers | Kies type “Bijstand”, voeg 2 medewerkers toe, sla op en heropen. | Beide medewerkers verschijnen opnieuw. |
| Zoeken op SIN | Voeg record toe met SIN `WXYZ0001` en zoek op `WXYZ`. | Record verschijnt in resultaten. |

## Automatische tests
Er is een voorbeeldtest in `tests/test_bijstand_insert.py` die controleert of bijstandsinvoer correct wordt opgeslagen. Voer de testreeks uit met:
```bash
pytest
```

## Kwaliteitsrichtlijnen
- Gebruik branches en pull requests voor elke wijziging.
- Laat code reviews uitvoeren door minimaal één collega.
- Houd deze wiki up-to-date bij wijzigingen in functionaliteit of UI.
