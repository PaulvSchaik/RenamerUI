# RenamerPro

RenamerPro is een intelligent script dat PDF bestanden automatisch hernoemt op basis van de inhoud.

## Hoe het werkt
1. Het script leest de eerste paar pagina's van een PDF bestand.
2. Het stuurt de tekst naar de Gemini AI om de datum, de betrokken partij en een korte samenvatting te bepalen.
3. Het bestand wordt hernoemd naar: `YYYY-MM - [Partij] - [Samenvatting].pdf`.

## Installatie

1. Zorg dat Python 3 geïnstalleerd is.
2. Installeer de benodigde bibliotheken:
   ```bash
   pip install -r requirements.txt
   ```
3. Kopieer `.env.example` naar `.env` en voeg je Google Gemini API key toe:
   ```bash
   cp .env.example .env
   # Bewerk .env en vul je API key in
   ```

## Gebruik

### Een map éénmalig scannen
```bash
python renamer.py --once /pad/naar/jouw/pdf_map
```

### Een map in de gaten houden (Watcher)
```bash
python renamer.py --watch /pad/naar/jouw/pdf_map
```

### Testen zonder echt te hernoemen (Dry Run)
```bash
python renamer.py --once /pad/naar/jouw/pdf_map --dry-run
```

## Vereisten
- Een Google Gemini API Key (gratis te verkrijgen via [Google AI Studio](https://aistudio.google.com/)).
