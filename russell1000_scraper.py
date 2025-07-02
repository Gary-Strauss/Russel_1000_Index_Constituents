import requests
import pandas as pd
from bs4 import BeautifulSoup
from io import StringIO
import logging
import os

# Logging konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def scrape_russell1000():
    url = "https://en.wikipedia.org/wiki/Russell_1000_Index"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Suche nach der "Components" Tabelle - versuche verschiedene Ansätze
    table = None
    
    # Versuche zuerst nach einer Tabelle mit "Components" im vorherigen Text zu suchen
    for heading in soup.find_all(['h2', 'h3']):
        if 'component' in heading.get_text().lower():
            table = heading.find_next('table')
            if table:
                break
    
    # Falls das nicht funktioniert, suche nach der größten wikitable
    if not table:
        tables = soup.find_all('table', {'class': 'wikitable'})
        if tables:
            # Nimm die größte Tabelle
            table = max(tables, key=lambda t: len(t.find_all('tr')))

    if not table:
        raise ValueError("Keine geeignete Tabelle gefunden.")

    logging.info(f"Tabelle gefunden mit {len(table.find_all('tr'))} Zeilen")

    # Extrahiere die Daten mit StringIO um die FutureWarning zu vermeiden
    table_html = str(table)
    df = pd.read_html(StringIO(table_html))[0]

    logging.info(f"DataFrame erstellt mit {len(df)} Zeilen und Spalten: {list(df.columns)}")

    # Spalten umbenennen - flexibler Ansatz
    column_mapping = {}
    for col in df.columns:
        col_lower = str(col).lower()
        if 'company' in col_lower or 'name' in col_lower:
            column_mapping[col] = 'Company'
        elif 'symbol' in col_lower or 'ticker' in col_lower:
            column_mapping[col] = 'Symbol'
        elif 'sector' in col_lower and 'sub' not in col_lower:
            column_mapping[col] = 'GICS_Sector'
        elif 'sub' in col_lower and 'industry' in col_lower:
            column_mapping[col] = 'GICS_Sub_Industry'

    logging.info(f"Spalten-Mapping: {column_mapping}")
    df.rename(columns=column_mapping, inplace=True)

    # Validierung - weniger strikt
    if len(df) < 100:
        raise ValueError(f"Die Anzahl der Unternehmen ({len(df)}) ist verdächtig niedrig.")

    logging.info(f"Validierung erfolgreich: {len(df)} Unternehmen gefunden")

    # Erstelle data Verzeichnis falls es nicht existiert
    os.makedirs('data', exist_ok=True)

    # Speichern der Daten
    csv_filename = "data/russell1000_constituents.csv"
    json_filename = "data/russell1000_constituents.json"
    df.to_csv(csv_filename, index=False)
    df.to_json(json_filename, orient='records')

    logging.info(f"Die Daten wurden erfolgreich in {csv_filename} und {json_filename} gespeichert.")

if __name__ == '__main__':
    scrape_russell1000()
