# -*- coding: utf-8 -*-
"""
Author: Sarah Hayat

This script provides a framework for constructing an equity investment strategy using stock market data. It includes:

1. **Ticker Retrieval**:
   - Fetches and merges tickers from S&P 500, Dow Jones, and Nasdaq-100 indices via web scraping.

2. **Data Processing**:
   - Downloads historical stock prices and financial data using `yfinance`.
   - Extracts and structures fundamental financial data (income statement, balance sheet, cash flow).
   - Data processing methods are adapted from Analyzing Alpha's yfinance Python tutorial: https://analyzingalpha.com/yfinance-python

3. **Growth Filtering**:
   - Identifies stocks with strong growth metrics, including revenue, EPS, ROE, and positive cash flow.

4. **Portfolio Weighting**:
   - Calculates market cap-based weights for selected stocks.

The output includes filtered tickers and their respective weights for portfolio construction or strategy testing.

"""

! pip install yfinance --upgrade --no-cache-dir

import yfinance as yf
import pandas as pd
import sys
import requests
from urllib.parse import quote
from bs4 import BeautifulSoup

def fetch_sp500_tickers():
    """
    Fetches the list of S&P 500 tickers from the Wikipedia page.

    Returns:
        list: A list of S&P 500 company tickers.
    """
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', {'id': 'constituents'})

    # Extract tickers using list comprehension
    tickers = [row.find_all('td')[0].text.strip() for row in table.find_all('tr')[1:]]
    return tickers

def get_dow_jones_tickers():
    """
    Fetches the list of Dow Jones Industrial Average tickers from Wikipedia.

    Returns:
        list: A list of ticker symbols.
    """

    url='https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average'

    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            table = soup.find('table', {'class': 'wikitable sortable'})
            tickers = []

            if table:
                for row in table.find_all('tr')[1:]:
                    cells = row.find_all('td')
                    if len(cells) > 0:
                        ticker = cells[1].get_text(strip=True)
                        tickers.append(ticker)
            return tickers
        else:
            print(f'Failed to retrieve the page. Status code: {response.status_code}')
            return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def get_nasdaq_100_ticker_symbols() -> list:
    """
    Extracts the Nasdaq-100 ticker symbols from the Wikipedia page.

    Returns:
        list: A list of Nasdaq-100 ticker symbols.
    """
    url = "https://en.wikipedia.org/wiki/Nasdaq-100"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all tables with the 'wikitable' class
    tables = soup.find_all('table', {'class': 'wikitable'})
    nasdaq_table = None

    # Locate the table containing 'Symbol' in the headers
    for table in tables:
        headers = table.find('tr')
        if headers and 'Symbol' in headers.text:
            nasdaq_table = table
            break

    # If no relevant table is found, return an empty list
    if nasdaq_table is None:
        print("Could not find the Nasdaq-100 table.")
        return []

    # Extract ticker symbols from the table
    ticker_symbols = []
    for row in nasdaq_table.find_all('tr')[1:]:
        cols = row.find_all('td')
        if len(cols) >= 2:
            symbol = cols[1].text.strip()
            ticker_symbols.append(symbol)

    return ticker_symbols

def merge_and_deduplicate_dynamic(*lists):
    """
    Merges dynamically passed lists and removes duplicates.

    Parameters:
        *lists: Variable number of lists passed as arguments.

    Returns:
        list: A deduplicated list containing elements from all input lists.
    """
    merged_set = set().union(*lists)
    return list(merged_set)

def common_info_keys(*tickers):
    key_sets = [set(yf.Ticker(ticker).info.keys()) for ticker in tickers]
    common_keys = set.intersection(*key_sets)

    return common_keys

#https://analyzingalpha.com/yfinance-python
def download(tickers, start=None, end=None, actions=False, threads=True,
             group_by='column', auto_adjust=False, back_adjust=False,
             progress=True, period="max", show_errors=True, interval="1d", prepost=False,
             proxy=None, rounding=False, timeout=None, **kwargs):
    """Download yahoo tickers
    :Parameters:
        tickers : str, list
            List of tickers to download
        period : str
            Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
            Either Use period parameter or use start and end
        interval : str
            Valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
            Intraday data cannot extend last 60 days
        start: str
            Download start date string (YYYY-MM-DD) or _datetime.
            Default is 1900-01-01
        end: str
            Download end date string (YYYY-MM-DD) or _datetime.
            Default is now
        group_by : str
            Group by 'ticker' or 'column' (default)
        prepost : bool
            Include Pre and Post market data in results?
            Default is False
        auto_adjust: bool
            Adjust all OHLC automatically? Default is False
        actions: bool
            Download dividend + stock splits data. Default is False
        threads: bool / int
            How many threads to use for mass downloading. Default is True
        proxy: str
            Optional. Proxy server URL scheme. Default is None
        rounding: bool
            Optional. Round values to 2 decimal places?
        show_errors: bool
            Optional. Doesn't print errors if True
        timeout: None or float
            If not None stops waiting for a response after given number of
            seconds. (Can also be a fraction of a second e.g. 0.01)
    """

def download_stock_data(tickers, start_date, end_date):
    data = yf.download(tickers, start=start_date, end=end_date, group_by='ticker')
    return data

def fetch_fundamental_data(tickers):
    """
    Fetch financial fundamental data (income statement, balance sheet, cash flow) for a list of tickers
    and combine them into a single DataFrame.

    Parameters:
    - tickers (list of str): List of stock tickers.

    Returns:
    - pd.DataFrame: Combined financial data with the outermost index as ticker and reset indices.
    """
    data = []

    for symbol in tickers:
        ticker = yf.Ticker(symbol)

        pnl = ticker.financials
        bs = ticker.balancesheet
        cf = ticker.cashflow

        fs = pd.concat([pnl, bs, cf])

        fs = fs.T
        fs['Ticker'] = symbol
        fs = fs.set_index(['Ticker'], append=True).swaplevel(0, 1)

        data.append(fs)

    final_df = pd.concat(data)
    final_df = final_df.reset_index()

    return final_df

def get_growth_filter(df):
    """
    Returns a Boolean series representing the growth filter criteria.

    Parameters:
        df (pd.DataFrame): The input DataFrame containing financial data.

    Returns:
        pd.Series: A Boolean series where True indicates rows that meet the growth criteria.
    """
    growth_filter = (
        (df['Total Revenue'] > df['Total Revenue'].shift(1)) &  # Revenue growth
        (df['Operating Income'] / df['Total Revenue'] > 0.10) &  # Operating income margin > 10%
        (df['EBITDA'] / df['Total Revenue'] > 0.10) &  # EBITDA margin > 10%
        (df['Diluted EPS'] > df['Diluted EPS'].shift(1)) &  # EPS growth
        (df['Net Debt'] / df['Stockholders Equity'] < 1) &  # Debt-to-Equity ratio < 1
        (df['Interest Expense'] < 0.1 * df['Operating Income']) &  # Interest Expense < 10% of EBIT
        (df['Free Cash Flow'] > 0) &  # Positive Free Cash Flow
        (df['Net Income'] / df['Stockholders Equity'] > 0.15) &  # ROE > 15%
        (df['Selling General And Administration'] / df['Total Revenue'] < 0.2) &  # SG&A as % of Revenue < 20%
        (df['Capital Expenditure'] / df['Total Revenue'] < 0.2)  # CapEx as % of Revenue < 20%
    )
    return growth_filter

def calculate_market_cap_weights(tickers):
    """
    Calculate percentage weights for stocks based on their market cap from Yahoo Finance.

    Args:
    - tickers (list of str): a list of stock ticker symbols.

    Returns:
    - list of lists: 2D array consisting of a list of inner arrays: [tickers, weights].
    """
    market_caps = {}

    for ticker in tickers:
        stock = yf.Ticker(ticker)
        market_cap = stock.info.get('marketCap')

        if market_cap:
            market_caps[ticker] = market_cap
        else:
            print(f"Market cap not available for {ticker}")

    total_market_cap = sum(market_caps.values())

    # 2D array
    ticker_weights = [
        [ticker, round((cap / total_market_cap) * 100, 2)]
        for ticker, cap in market_caps.items()
    ]

    return ticker_weights

sp_500_tickers = fetch_sp500_tickers()
dow_jones_tickers = get_dow_jones_tickers()
nasdaq_tickers = get_nasdaq_100_ticker_symbols()
tickers = merge_and_deduplicate_dynamic(nasdaq_tickers, sp_500_tickers, dow_jones_tickers)

#making some unsual symbols compatible with yahoo api
tickers = [ticker.replace('.', '-') if ticker in ("BRK.B", "BF.B") else ticker for ticker in tickers]

data = download_stock_data(tickers, "2004-01-01", "2024-11-11")
#print(data.tail())

final_df = fetch_fundamental_data(tickers)
#print(final_df)
#print(final_df.columns.tolist())

growth_filter = get_growth_filter(final_df)
selected_tickers = final_df[growth_filter]['Ticker'].unique()
#print(len(selected_tickers))
#print(selected_tickers)
weights = calculate_market_cap_weights(selected_tickers)

print("Ticker, Weights:")
for item in weights:
    print(item)
