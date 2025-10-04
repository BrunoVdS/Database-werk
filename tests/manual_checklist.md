# Manual Regression Checklist

## Invalid SIN edit is rejected
1. Start de applicatie en open het tabblad **Bewerken**.
2. Selecteer een bestaand record met een geldig SIN (bijvoorbeeld `ABCD1234`).
3. Pas het SIN-veld aan naar een ongeldig formaat, zoals `A1C3`.
4. Klik op **Bijwerken** en bevestig dat een foutvenster verschijnt met de melding dat het SIN exact vier letters en vier cijfers moet bevatten.
5. Sluit het dialoogvenster, laad het record opnieuw en controleer dat het oorspronkelijke SIN ongewijzigd is gebleven in de database.
