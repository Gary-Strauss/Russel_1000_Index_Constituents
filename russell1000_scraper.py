import requests
import pandas as pd
from bs4 import BeautifulSoup

def scrape_russell1000():
    url = "https://en.wikipedia.org/wiki/Russell_1000_Index"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Suche nach der "Components" Tabelle
    table = soup.find('table', {'class': 'wikitable'})

    # Extrahiere die Daten
    df = pd.read_html(str(table))[0]

    # Spalten umbenennen
    column_mapping = {
        'Company': 'Company',
        'Symbol': 'Ticker', 
        'GICS Sector': 'GICS_Sector',
        'GICS Sub-Industry': 'GICS_Sub_Industry'
    }
    df.rename(columns=column_mapping, inplace=True)

    # Validierung
    if len(df) < 900:
        raise ValueError("Die Anzahl der Unternehmen ist weniger als 900.")

    # Speichern der Daten
    csv_filename = "data/russell1000_constituents.csv"
    json_filename = "data/russell1000_constituents.json"
    df.to_csv(csv_filename, index=False)
    df.to_json(json_filename, orient='records')

    print(f"Die Daten wurden erfolgreich in {csv_filename} und {json_filename} gespeichert.")

if __name__ == '__main__':
    scrape_russell1000()
