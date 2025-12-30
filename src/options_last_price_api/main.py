import re
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
import yfinance as yf
import pandas as pd

from options_last_price_api.security import get_api_key

app = FastAPI(
    title="Financial Data API",
    description="Provides option prices and upcoming earnings dates.",
    version="1.1.0",
)

# --- Data Models ---

class PriceResponse(BaseModel):
    contract_symbol: str
    last_price: float
    message: str = "Price fetched successfully."

class EarningsDateResponse(BaseModel):
    ticker: str
    earnings_date: Optional[str]
    days_to_earnings: Optional[int]
    message: str

# --- Utility Functions ---

def parse_ticker_from_symbol(symbol: str) -> str:
    """
    Extracts the base stock ticker from various formats:
    1. Stock Ticker: AAPL -> AAPL
    2. TOS Option: .AAPL251219C200 -> AAPL
    3. Yahoo Option: AAPL251219C00200000 -> AAPL
    """
    symbol = symbol.strip().upper()
    
    # Check for Thinkorswim format (starts with .)
    if symbol.startswith('.'):
        # Regex to capture ticker after the dot
        tos_match = re.match(r'^\.([A-Z]+)', symbol)
        if tos_match:
            return tos_match.group(1)
            
    # Check for Yahoo Option format (Ticker + 6 digits + C/P + 8 digits)
    # The date/type marker (\d{6}[CP]) is a reliable anchor
    yahoo_opt_match = re.search(r'([A-Z]+)\d{6}[CP]', symbol)
    if yahoo_opt_match:
        return yahoo_opt_match.group(1)
    
    # Otherwise, assume it's just the ticker
    return symbol

def fetch_earnings_data(ticker: str) -> dict:
    """
    Fetches the next earnings date for a given ticker.
    """
    try:
        # Extract the base ticker in case an option symbol was passed
        base_ticker = parse_ticker_from_symbol(ticker)
        stock = yf.Ticker(base_ticker)
        
        # 1. Try stock.calendar
        calendar = stock.calendar
        if calendar is not None and calendar != {}:
            earnings_dates = calendar.get('Earnings Date')
            if earnings_dates is not None:
                next_date = earnings_dates[0]
                today = datetime.now().date()
                days_diff = (next_date - today).days
                
                return {
                    "ticker": base_ticker,
                    "earnings_date": next_date.strftime('%Y-%m-%d'),
                    "days_to_earnings": days_diff,
                    "message": "Successfully retrieved earnings date."
                }

        # 2. Fallback to .info metadata
        info_date = stock.info.get('earningsNext')
        if info_date:
            dt = datetime.fromtimestamp(info_date)
            today = datetime.now()
            days_diff = (dt.date() - today.date()).days
            return {
                "ticker": base_ticker,
                "earnings_date": dt.strftime('%Y-%m-%d'),
                "days_to_earnings": days_diff,
                "message": "Retrieved from info metadata."
            }

        return {
            "ticker": base_ticker,
            "earnings_date": None,
            "days_to_earnings": None,
            "message": "No upcoming earnings date found."
        }
    except Exception as e:
        return {
            "ticker": ticker.upper(),
            "earnings_date": None,
            "days_to_earnings": None,
            "message": f"Error: {str(e)}"
        }

# --- API Endpoints ---

@app.get(
    "/option-price/{option_symbol}", 
    response_model=PriceResponse, 
    dependencies=[Depends(get_api_key)]
)
async def get_last_option_price(option_symbol: str):
    """Fetches the last traded price for a specific option contract."""
    try:
        # Ticker parsing for option fetch
        yahoo_opt_match = re.search(r'([A-Z]+)(\d{6}[CP])', option_symbol.upper())
        if not yahoo_opt_match:
             raise ValueError("Invalid Yahoo option symbol format.")
             
        ticker = yahoo_opt_match.group(1)
        date_str = yahoo_opt_match.group(2)[:6]
        expiration_date = datetime.strptime(date_str, '%y%m%d').strftime('%Y-%m-%d')
        
        stock = yf.Ticker(ticker)
        if expiration_date not in stock.options:
            raise HTTPException(status_code=404, detail=f"Expiration {expiration_date} not found.")
        
        chain = stock.option_chain(expiration_date)
        all_options = pd.concat([chain.calls, chain.puts])
        target = all_options[all_options['contractSymbol'] == option_symbol.upper()]
        
        if target.empty:
            raise HTTPException(status_code=404, detail="Contract not found.")
            
        return PriceResponse(
            contract_symbol=option_symbol,
            last_price=float(target['lastPrice'].iloc[0])
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get(
    "/earnings-date/{identifier}", 
    response_model=EarningsDateResponse, 
    dependencies=[Depends(get_api_key)]
)
async def get_earnings_date(identifier: str):
    """
    Retrieves the next expected earnings date. 
    Accepts stock tickers (AAPL) or option symbols (.AAPL251219C200).
    """
    return fetch_earnings_data(identifier)

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "API is running."}
