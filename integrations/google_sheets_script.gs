/**
 * Custom function to fetch option pricing data from a FastAPI server.
 *
 * @param {string} optionSymbol The standardized option symbol (e.g., 'TSLA251219C00200000').
 * @return {Array<Array<string | number>>} A 2D array containing header and data rows.
 * @customfunction
 */
function FETCH_OPTION_DATA(optionSymbol) {
  
  apiKey = 'tk1'
  apiUrlBase = 'http://dev.malctaylor15.com:2524'
  if (!optionSymbol || !apiUrlBase || !apiKey) {
    return [["ERROR", "All parameters must be provided"]];
  }

  const url = `${apiUrlBase}/option-price/${optionSymbol}`;
  
  const options = {
    'method': 'get',
    'contentType': 'application/json',
    'headers': {
      // MANDATORY: Pass the API key using the required header name
      'X-API-Key': apiKey 
    },
    'muteHttpExceptions': true // Prevents script from crashing on 4xx/5xx errors
  };

  try {
    const response = UrlFetchApp.fetch(url, options);
    const responseCode = response.getResponseCode();
    const jsonText = response.getContentText();
    
    // Check for success (200 OK)
    if (responseCode === 200) {
      const data = JSON.parse(jsonText);
      
      // Define the headers and data structure for easy sheet integration
      const headers = ["Symbol", "Price", "Yahoo Link", "Details", "Status"];
      const values = [
        data.contract_symbol, 
        data.last_price, 
        data.message,
        "Success"
      ];
      
      return [headers, values];
      
    } else {
      // Handle API errors (e.g., 403 Forbidden, 404 Not Found)
      const errorData = JSON.parse(jsonText);
      const errorMessage = errorData.detail || `HTTP Error ${responseCode}`;
      
      return [["Symbol", "Price", "Error Details"], [optionSymbol, 0, errorMessage]];
    }
  } catch (e) {
    // Handle network or JSON parsing errors
    return [["ERROR", "Network Failure", "Details"], [optionSymbol, e.toString(), ""]];
  }
}



/**
 * Custom function to fetch option pricing data and return ONLY the last price.
 *
 * @param {string} optionSymbol The standardized option symbol (e.g., 'TSLA251219C00200000').
 * @return {number | string} The last price of the option or an error message string.
 * @customfunction
 */
function GET_LAST_PRICE(optionSymbol) {
  
  // Use the same hardcoded credentials as FETCH_OPTION_DATA
  apiKey = 'tk1'
  apiUrlBase = 'http://dev.malctaylor15.com:2524'
  
  if (!optionSymbol || !apiUrlBase || !apiKey) {
    return "ERROR: Missing symbol, API base URL, or API key.";
  }

  const url = `${apiUrlBase}/option-price/${optionSymbol}`;
  
  const options = {
    'method': 'get',
    'contentType': 'application/json',
    'headers': {
      'X-API-Key': apiKey 
    },
    'muteHttpExceptions': true
  };

  try {
    const response = UrlFetchApp.fetch(url, options);
    const responseCode = response.getResponseCode();
    const jsonText = response.getContentText();
    
    if (responseCode === 200) {
      const data = JSON.parse(jsonText);
      
      // Return only the last_price field as a number
      if (typeof data.last_price === 'number') {
        return data.last_price;
      }
      return "ERROR: 'last_price' field not found or is not a number.";
      
    } else {
      // Handle API errors
      const errorData = JSON.parse(jsonText);
      const errorMessage = errorData.detail || `HTTP Error ${responseCode}`;
      
      return `API ERROR: ${errorMessage}`;
    }
  } catch (e) {
    // Handle network errors
    return `NETWORK ERROR: ${e.toString()}`;
  }
}



