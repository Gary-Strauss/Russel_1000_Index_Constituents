import pytest
import pandas as pd
from bs4 import BeautifulSoup
from unittest.mock import Mock, patch, mock_open
import requests
from io import StringIO
import os

from russell1000_scraper import (
    fetch_webpage,
    find_russell_table,
    process_dataframe,
    validate_data,
    save_data,
    scrape_russell1000
)


class TestFetchWebpage:
    """Tests for fetch_webpage function."""

    @patch('russell1000_scraper.requests.get')
    def test_fetch_webpage_success(self, mock_get):
        """Test successful webpage fetch."""
        # Mock response
        mock_response = Mock()
        mock_response.text = '<html><body><h1>Test</h1></body></html>'
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # Call function
        result = fetch_webpage('https://example.com')

        # Assertions
        assert isinstance(result, BeautifulSoup)
        mock_get.assert_called_once()
        assert 'User-Agent' in mock_get.call_args[1]['headers']

    @patch('russell1000_scraper.requests.get')
    def test_fetch_webpage_timeout(self, mock_get):
        """Test timeout handling."""
        mock_get.side_effect = requests.exceptions.Timeout()

        with pytest.raises(requests.exceptions.Timeout):
            fetch_webpage('https://example.com')

    @patch('russell1000_scraper.requests.get')
    def test_fetch_webpage_connection_error(self, mock_get):
        """Test connection error handling."""
        mock_get.side_effect = requests.exceptions.ConnectionError()

        with pytest.raises(requests.exceptions.ConnectionError):
            fetch_webpage('https://example.com')


class TestFindRussellTable:
    """Tests for find_russell_table function."""

    def test_find_table_with_components_heading(self):
        """Test finding table after 'Components' heading."""
        html = """
        <html>
            <body>
                <h2>Components</h2>
                <table class="wikitable">
                    <tr><th>Company</th><th>Symbol</th><th>GICS Sector</th><th>GICS Sub-Industry</th></tr>
                    <tr><td>Apple Inc.</td><td>AAPL</td><td>Technology</td><td>Computers</td></tr>
                    <tr><td>Microsoft Corp</td><td>MSFT</td><td>Technology</td><td>Software</td></tr>
                </table>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        df = find_russell_table(soup)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert 'Company' in df.columns or 'Symbol' in df.columns

    def test_find_largest_wikitable(self):
        """Test finding largest wikitable when no 'Components' heading."""
        html = """
        <html>
            <body>
                <table class="wikitable">
                    <tr><th>Col1</th></tr>
                    <tr><td>Data1</td></tr>
                </table>
                <table class="wikitable">
                    <tr><th>Company</th><th>Symbol</th></tr>
                    <tr><td>Apple</td><td>AAPL</td></tr>
                    <tr><td>Microsoft</td><td>MSFT</td></tr>
                    <tr><td>Google</td><td>GOOGL</td></tr>
                </table>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        df = find_russell_table(soup)

        assert isinstance(df, pd.DataFrame)
        assert len(df) >= 2

    def test_no_table_found(self):
        """Test error when no table is found."""
        html = "<html><body><p>No tables here</p></body></html>"
        soup = BeautifulSoup(html, 'html.parser')

        with pytest.raises(ValueError, match="No suitable table found"):
            find_russell_table(soup)


class TestProcessDataframe:
    """Tests for process_dataframe function."""

    def test_process_dataframe_standard_columns(self):
        """Test processing DataFrame with standard column names."""
        df = pd.DataFrame({
            'Company Name': ['Apple Inc.', 'Microsoft Corp'],
            'Ticker Symbol': ['AAPL', 'MSFT'],
            'GICS Sector': ['Technology', 'Technology'],
            'GICS Sub-Industry': ['Computers', 'Software']
        })

        result = process_dataframe(df)

        assert 'Company' in result.columns
        assert 'Symbol' in result.columns
        assert 'GICS_Sector' in result.columns
        assert 'GICS_Sub_Industry' in result.columns

    def test_process_dataframe_lowercase_columns(self):
        """Test processing DataFrame with lowercase column names."""
        df = pd.DataFrame({
            'company': ['Apple Inc.'],
            'symbol': ['AAPL'],
            'sector': ['Technology'],
            'sub industry': ['Computers']
        })

        result = process_dataframe(df)

        assert 'Company' in result.columns
        assert 'Symbol' in result.columns
        assert 'GICS_Sector' in result.columns
        assert 'GICS_Sub_Industry' in result.columns


class TestValidateData:
    """Tests for validate_data function."""

    def test_validate_data_success(self):
        """Test validation with sufficient data."""
        df = pd.DataFrame({'Company': ['Company' + str(i) for i in range(150)]})

        # Should not raise any exception
        validate_data(df)

    def test_validate_data_too_few_companies(self):
        """Test validation fails with too few companies."""
        df = pd.DataFrame({'Company': ['Apple', 'Microsoft']})

        with pytest.raises(ValueError, match="suspiciously low"):
            validate_data(df)


class TestSaveData:
    """Tests for save_data function."""

    @patch('russell1000_scraper.os.makedirs')
    @patch('pandas.DataFrame.to_csv')
    @patch('pandas.DataFrame.to_json')
    def test_save_data_success(self, mock_to_json, mock_to_csv, mock_makedirs):
        """Test successful data saving."""
        df = pd.DataFrame({
            'Company': ['Apple Inc.', 'Microsoft Corp'],
            'Symbol': ['AAPL', 'MSFT']
        })

        save_data(df)

        mock_makedirs.assert_called_once_with('data', exist_ok=True)
        mock_to_csv.assert_called_once_with('data/russell1000_constituents.csv', index=False)
        mock_to_json.assert_called_once_with('data/russell1000_constituents.json', orient='records')

    @patch('russell1000_scraper.os.makedirs')
    @patch('pandas.DataFrame.to_csv')
    def test_save_data_csv_error(self, mock_to_csv, mock_makedirs):
        """Test handling of CSV save error."""
        df = pd.DataFrame({'Company': ['Apple Inc.']})
        mock_to_csv.side_effect = OSError("Permission denied")

        with pytest.raises(OSError):
            save_data(df)

    @patch('russell1000_scraper.os.makedirs')
    @patch('pandas.DataFrame.to_csv')
    @patch('pandas.DataFrame.to_json')
    def test_save_data_json_error(self, mock_to_json, mock_to_csv, mock_makedirs):
        """Test handling of JSON save error."""
        df = pd.DataFrame({'Company': ['Apple Inc.']})
        mock_to_json.side_effect = IOError("Disk full")

        with pytest.raises(IOError):
            save_data(df)


class TestScrapeRussell1000:
    """Integration tests for scrape_russell1000 function."""

    @patch('russell1000_scraper.save_data')
    @patch('russell1000_scraper.validate_data')
    @patch('russell1000_scraper.process_dataframe')
    @patch('russell1000_scraper.find_russell_table')
    @patch('russell1000_scraper.fetch_webpage')
    def test_scrape_russell1000_integration(self, mock_fetch, mock_find, mock_process, mock_validate, mock_save):
        """Test complete scraping workflow."""
        # Setup mocks
        mock_soup = Mock()
        mock_fetch.return_value = mock_soup

        mock_df = pd.DataFrame({
            'Company': ['Apple Inc.'] * 150,
            'Symbol': ['AAPL'] * 150
        })
        mock_find.return_value = mock_df
        mock_process.return_value = mock_df

        # Run scraper
        scrape_russell1000()

        # Verify all steps were called
        mock_fetch.assert_called_once()
        mock_find.assert_called_once_with(mock_soup)
        mock_process.assert_called_once()
        mock_validate.assert_called_once()
        mock_save.assert_called_once()
