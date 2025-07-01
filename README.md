# Russell 1000 Scraper

Ein Python-Tool zum Abrufen und Speichern der aktuellen Russell 1000 Bestandteile von Wikipedia.

## Beschreibung

Dieses Projekt scrapt die Liste der Russell 1000 Unternehmen von der Wikipedia-Seite...

**CSV Format:**
https://raw.githubusercontent.com/Gary-Strauss/russell1000-scraper/main/data/russell1000_constituents.csv

**JSON Format:**
https://raw.githubusercontent.com/Gary-Strauss/russell1000-scraper/main/data/russell1000_constituents.json

## Datenstruktur

Die extrahierten Daten enthalten folgende Spalten:
- **Symbol**: Unternehmens-Aktiensymbol
- **Company**: Vollständiger Unternehmensname  
- **GICS_Sector**: Global Industry Classification Standard Sektor
- **GICS_Sub_Industry**: GICS Unter-Industrie

Das Tool extrahiert derzeit etwa 1.000 Unternehmen, einschließlich (01.07.2025):
- Apple Inc. (AAPL) - Information Technology
- Nvidia (NVDA) - Information Technology
- Microsoft (MSFT) - Information Technology
