# RenamerUI

RenamerUI is een macOS-applicatie die PDF-bestanden automatisch hernoemt op basis van hun inhoud. De app gebruikt Google Gemini AI om de datum, betrokken partij en een korte omschrijving uit het document te halen en maakt daar een duidelijke bestandsnaam van.

**Voorbeeld:** `factuur.pdf` → `2024-11 - Belastingdienst - Aangifte inkomstenbelasting.pdf`

---

## Hoe het werkt

1. Je selecteert een map met PDF-bestanden.
2. De app leest de eerste pagina's van elk PDF-bestand.
3. De tekst wordt naar Google Gemini gestuurd, die de volgende gegevens extraheert:
   - **Datum** van het document (jaar en maand)
   - **Betrokken partij** (bijv. bedrijfsnaam, afzender)
   - **Korte omschrijving** van de inhoud
4. Het bestand wordt hernoemd naar het formaat: `YYYY-MM - [Partij] - [Omschrijving].pdf`

---

## Vereisten

- macOS 12 of nieuwer
- Een gratis Google Gemini API-sleutel ([aanmaken via Google AI Studio](https://aistudio.google.com/app/apikey))

---

## Installatie

### Optie 1 — Kant-en-klare app (aanbevolen)

Download `RenamerUI.app` en sleep deze naar je map `Programma's` (`/Applications`).

Bij het eerste openen vraagt macOS mogelijk om bevestiging omdat de app niet via de App Store is geïnstalleerd. Ga naar **Systeeminstellingen → Privacy en beveiliging** en klik op **Toch openen**.

### Optie 2 — Zelf bouwen vanuit de broncode

Vereisten: Python 3.11 of nieuwer.

```bash
git clone https://github.com/PaulvSchaik/RenamerUI.git
cd RenamerUI

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

./build_app.sh
```

De app verschijnt daarna in de map `dist/RenamerUI.app`.

---

## Gebruik

### 1. API-sleutel instellen

Bij het eerste gebruik klik je op **⚙ Instellingen** (rechtsboven) en voer je jouw Google Gemini API-sleutel in. De sleutel wordt veilig opgeslagen op je Mac en hoeft maar één keer te worden ingevuld.

### 2. Map selecteren

Klik op **📁 Kies map…** en selecteer de map met de PDF-bestanden die je wilt hernoemen.

### 3. Hernoemen

Klik op **▶ Start hernoeming**. De app verwerkt alle PDF-bestanden in de geselecteerde map en toont de voortgang in het logboek.

### Dry-run

Zet het vinkje **Dry-run** aan om eerst te bekijken welke nieuwe namen de app zou gebruiken, zonder de bestanden daadwerkelijk te hernoemen. Handig om de resultaten te controleren voordat je de wijzigingen doorvoert.

---

## Instellingen

De instellingen (API-sleutel) worden opgeslagen op:

```
~/Library/Application Support/RenamerUI/settings.json
```

---

## Technische details

| Onderdeel | Technologie |
|---|---|
| GUI | Python + CustomTkinter |
| PDF-verwerking | PyMuPDF |
| AI | Google Gemini 2.5 Flash |
| Bundeling | PyInstaller |

De app ondersteunt automatisch de lichte en donkere weergave van macOS.
