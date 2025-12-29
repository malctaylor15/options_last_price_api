import re
import os
from datetime import datetime
from dotenv import load_dotenv

from fastapi import FastAPI, Depends, HTTPException, status, Security
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
import yfinance as yf
import pandas as pd

# Load environment variables (like the API key) from a .env file
# NOTE: In a real cloud environment, use dedicated secrets management.
load_dotenv()

# --- Configuration & Authentication Setup ---
# The secret API key is read from the environment variable 'SECRET_API_KEY'
# CHANGE THIS TO A REAL, LONG, RANDOM KEY in your .env file or cloud environment
API_KEY = os.getenv("SECRET_API_KEY", "tk1") 

# Define the header where the client must send the API key (e.g., X-API-Key: YOUR_KEY)
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

app = FastAPI(
    title="Option Price Fetcher API",
    description="Fetches the last traded price for an option contract from Yahoo Finance.",
    version="1.0.0",
)

class PriceResponse(BaseModel):
    """Defines the structure of a successful API response."""
    contract_symbol: str
    last_price: float
    message: str = "Price fetched successfully."

def get_api_key(api_key: str = Security(api_key_header)):
    """Dependency function to validate the API key."""
    if api_key == API_KEY:
        return api_key
    # Raise a 401 Unauthorized error if the key is invalid
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API Key. Access denied.",
    )

# --- Utility Functions for Parsing and Fetching ---

def parse_option_symbol(symbol: str):
    """
    Parses a standard Yahoo Finance option contract symbol (e.g., AAPL251231C0150000)
    to extract the underlying ticker and expiration date.
    """
    # Pattern to find the date (6 digits: YYMMDD) followed by the type (C/P)
    # The date/type marker is always 7 characters long.
    match = re.search(r'(\d{6}[CP])', symbol)
    
    if not match:
        raise ValueError("Invalid option symbol format. Expected YYMMDDC or YYMMDDP.")

    date_type_start_index = match.start(1)
    
    ticker = symbol[:date_type_start_index].upper()
    date_str = symbol[date_type_start_index : date_type_start_index + 6]
    
    # Format expiration date for yfinance (YYYY-MM-DD)
    # Assuming the YY is for the 21st century (20xx).
    try:
        # yfinance expects the date in 'YYYY-MM-DD' format, 
        # but only as a valid date in its available options list.
        # We parse it to ensure it's a valid date structure before fetching.
        expiration_date = datetime.strptime(date_str, '%y%m%d').strftime('%Y-%m-%d')
    except ValueError:
        raise ValueError(f"Invalid date found in symbol: {date_str}. Must be YYMMDD.")
        
    return ticker, expiration_date

@app.get(
    "/option-price/{option_symbol}", 
    response_model=PriceResponse, 
    dependencies=[Depends(get_api_key)]
)
async def get_last_option_price(option_symbol: str):
    """
    Fetches the last traded price for a specific option contract.
    The request must include a valid API key in the 'X-API-Key' header.
    """
    try:
        # 1. Parse the symbol to get the Ticker and Expiration
        ticker, expiration_date = parse_option_symbol(option_symbol)
        
        # 2. Initialize yfinance Ticker object
        stock = yf.Ticker(ticker)

        # 3. Check if the expiration date is available
        if expiration_date not in stock.options:
            available_dates = stock.options
            if not available_dates:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, 
                    detail=f"No option chain found for ticker {ticker}. Check if it's correct."
                )
            
            # Show the user the closest available dates if the requested one is not found
            suggestion = f"Available dates: {', '.join(available_dates[:5])}..."
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Expiration date {expiration_date} not available for {ticker}. {suggestion}"
            )
        
        # 4. Fetch the entire option chain for that date
        option_chain = stock.option_chain(expiration_date)
        
        # Combine calls and puts into a single DataFrame
        all_options: pd.DataFrame = pd.concat([option_chain.calls, option_chain.puts])
        
        # 5. Filter for the exact contract symbol
        target_option = all_options[all_options['contractSymbol'] == option_symbol]
        
        if target_option.empty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Contract symbol '{option_symbol}' not found in the option chain."
            )
            
        # 6. Extract the last traded price
        last_price = target_option['lastPrice'].iloc[0]

        if pd.isna(last_price) or last_price is None:
             raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Price data not available for '{option_symbol}'."
            )

        return PriceResponse(
            contract_symbol=option_symbol,
            last_price=float(last_price)
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Input Error: {e}"
        )
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing the request. Try again later. Details: {e}"
        )

# Simple health check endpoint (no auth needed)
@app.get("/health")
def health_check():
    return {"status": "ok", "message": "API is running."}
