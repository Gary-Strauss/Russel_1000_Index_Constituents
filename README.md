# Russell 1000 Index Scraper 📈

Dieses Repository enthält einen Python-Scraper, der die Liste der im **Russell 1000 Index** enthaltenen Unternehmen extrahiert.

**Datenquelle:** [Wikipedia - Russell 1000 Index](https://en.wikipedia.org/wiki/Russell_1000_Index)

---

## 📋 Projektübersicht

Das Hauptziel dieses Projekts ist es, eine aktuelle und leicht zugängliche Liste der Unternehmen des Russell 1000 Index bereitzustellen. Der Scraper `russell1000_scraper.py` besucht die entsprechende Wikipedia-Seite, parst die Tabelle der Index-Komponenten und speichert die Daten in den Formaten CSV und JSON.

Ein automatisierter **GitHub Actions Workflow** sorgt dafür, dass die Daten wöchentlich aktualisiert werden.

---

## 🗃️ Die Daten

Der Scraper generiert zwei Dateien im `data/`-Verzeichnis:

* `data/russell1000_constituents.csv`
* `data/russell1000_constituents.json`

Die Daten enthalten die folgenden Spalten:

| Spalte              | Beschreibung                                     |
| ------------------- | ------------------------------------------------ |
| `Company`           | Name des Unternehmens                            |
| `Symbol`            | Börsenkürzel (Ticker)                            |
| `GICS_Sector`       | GICS-Sektor des Unternehmens                     |
| `GICS_Sub_Industry` | GICS-Sub-Industrie (detailliertere Klassifikation) |

---

## 🤖 Automatisierung

Ein GitHub Actions Workflow, definiert in `.github/workflows/update-russell1000.yml`, automatisiert den Scraping-Prozess.

* **Zeitplan:** Der Workflow läuft automatisch **jeden Sonntag um 06:00 Uhr UTC**.
* **Prozess:**
    1.  Startet eine virtuelle Umgebung.
    2.  Installiert die notwendigen Python-Pakete aus `requirements.txt`.
    3.  Führt das Skript `russell1000_scraper.py` aus.
    4.  Überprüft, ob die Daten sich geändert haben.
    5.  Falls ja, werden die neuen Daten-Dateien automatisch in das Repository committet und gepusht.
* **Manuelle Ausführung:** Der Workflow kann auch jederzeit manuell über den "Actions"-Tab des Repositories gestartet werden.

---

## 🚀 Lokale Ausführung

Um den Scraper lokal auszuführen, befolge diese Schritte:

1.  **Repository klonen:**
    ```bash
    git clone [https://github.com/Gary-Strauss/Russel_1000_Index_Constituents.git](https://github.com/Gary-Strauss/Russel_1000_Index_Constituents.git)
    cd Russel_1000_Index_Constituents
    ```

2.  **Abhängigkeiten installieren:** (Es wird empfohlen, eine virtuelle Umgebung zu verwenden)
    ```bash
    pip install -r requirements.txt
    ```

3.  **Scraper ausführen:**
    ```bash
    python russell1000_scraper.py
    ```
    Nach der Ausführung findest du die aktualisierten `csv`- und `json`-Dateien im `data/`-Verzeichnis.

---

## 📄 Lizenz

Dieses Projekt steht unter der **MIT-Lizenz**. Details findest du in der `LICENSE`-Datei.
