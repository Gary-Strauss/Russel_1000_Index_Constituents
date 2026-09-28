import requests
import pandas as pd
from bs4 import BeautifulSoup
from io import StringIO
import logging
import os

# Configure logging
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(level=getattr(logging, log_level), format='%(asctime)s - %(levelname)s - %(message)s')


def fetch_webpage(url):
    """Fetch webpage content and return BeautifulSoup object."""
    try:
        headers = {'User-Agent': 'Russell1000-Scraper/1.0 (Educational Purpose)'}
        response = requests.get(url, timeout=10, headers=headers)
        response.raise_for_status()  # Raises exception for HTTP errors
    except requests.exceptions.Timeout:
        logging.error(f"Timeout while fetching URL: {url}")
        raise
    except requests.exceptions.ConnectionError:
        logging.error(f"Connection error while fetching URL: {url}")
        raise
    except requests.exceptions.RequestException as e:
        logging.error(f"HTTP request error: {e}")
        raise
    
    return BeautifulSoup(response.text, 'html.parser')


def _header_texts(table):
    """Return the lower-cased header cell texts of a table."""
    first_row = table.find('tr')
    if not first_row:
        return []
    return [cell.get_text(strip=True).lower() for cell in first_row.find_all(['th', 'td'])]


def _is_constituents_table(table):
    """A constituents table must have a symbol/ticker column."""
    return any('symbol' in h or 'ticker' in h for h in _header_texts(table))


def find_russell_table(soup):
    """Find and extract the Russell 1000 components table from the webpage."""
    # Only tables with a symbol/ticker column are candidates. This prevents
    # silently picking unrelated tables such as the annual returns table.
    tables = soup.find_all('table', {'class': 'wikitable'}) or soup.find_all('table')
    candidates = [t for t in tables if _is_constituents_table(t)]

    if not candidates:
        raise ValueError("No suitable table found.")

    # Take the largest candidate; if the list is split into several tables
    # with identical headers (e.g. alphabetical sections), combine them.
    largest = max(candidates, key=lambda t: len(t.find_all('tr')))
    headers = _header_texts(largest)
    selected = [t for t in candidates if _header_texts(t) == headers]

    logging.info(f"{len(selected)} table(s) found with {sum(len(t.find_all('tr')) for t in selected)} rows")

    # Extract data with StringIO to avoid FutureWarning
    frames = [pd.read_html(StringIO(str(t)))[0] for t in selected]
    df = pd.concat(frames, ignore_index=True) if len(frames) > 1 else frames[0]

    logging.info(f"DataFrame created with {len(df)} rows and columns: {list(df.columns)}")
    
    return df


def process_dataframe(df):
    """Clean and rename DataFrame columns."""
    # Rename columns - flexible approach
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

    logging.info(f"Column mapping: {column_mapping}")
    df.rename(columns=column_mapping, inplace=True)
    
    return df


def validate_data(df):
    """Validate the extracted data."""
    if 'Symbol' not in df.columns:
        raise ValueError(f"No 'Symbol' column found in columns: {list(df.columns)}")

    # Validation - less strict
    if len(df) < 100:
        raise ValueError(f"The number of companies ({len(df)}) is suspiciously low.")

    logging.info(f"Validation successful: {len(df)} companies found")


def save_data(df):
    """Save DataFrame to CSV and JSON files."""
    # Create data directory if it doesn't exist
    try:
        os.makedirs('data', exist_ok=True)
        logging.info("Data directory created or already exists")
    except OSError as e:
        logging.error(f"Failed to create data directory: {e}")
        raise

    # Save the data
    csv_filename = "data/russell1000_constituents.csv"
    json_filename = "data/russell1000_constituents.json"
    
    try:
        df.to_csv(csv_filename, index=False)
        logging.info(f"Data successfully saved to {csv_filename}")
    except (OSError, IOError, PermissionError) as e:
        logging.error(f"Failed to save CSV file {csv_filename}: {e}")
        raise
    
    try:
        df.to_json(json_filename, orient='records')
        logging.info(f"Data successfully saved to {json_filename}")
    except (OSError, IOError, PermissionError) as e:
        logging.error(f"Failed to save JSON file {json_filename}: {e}")
        raise

    logging.info(f"Data successfully saved to both {csv_filename} and {json_filename}")


def scrape_russell1000():
    """Main function to orchestrate the Russell 1000 scraping process."""
    url = "https://en.wikipedia.org/wiki/List_of_Russell_1000_companies"
    
    # Fetch webpage
    soup = fetch_webpage(url)
    
    # Find and extract table
    df = find_russell_table(soup)
    
    # Process DataFrame
    df = process_dataframe(df)
    
    # Validate data
    validate_data(df)
    
    # Save data
    save_data(df)


if __name__ == '__main__':
    try:
        scrape_russell1000()
    except Exception as e:
        logging.error(f"Scraping failed: {e}")
        raise
