# Import yahoo finance 
import yfinance as yf
# Bring in colorama for fancy printing
from colorama import Fore
# Bring in MCP Server SDK
from mcp.server.fastmcp import FastMCP
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
# Create server 
mcp = FastMCP("yfinanceserver")

# # Build server function
@mcp.tool()
def stock_price(stock_ticker: str) -> str:
    """This tool returns the last known price for a given stock ticker.
    Args:
        stock_ticker: a alphanumeric stock ticker 
        Example payload: "NVDA"

    Returns:
        str:"Ticker: Last Price" 
        Example Respnse "NVDA: $100.21" 
        """
    # Specify stock ticker 
    dat = yf.Ticker(stock_ticker)
    # Get historical prices
    historical_prices = dat.history(period='1mo')
    # Filter on closes only
    last_months_closes = historical_prices['Close']
    print(Fore.YELLOW + str(last_months_closes))
    return str(f"Stock price over the last month for {stock_ticker}: {last_months_closes}")

@mcp.tool()
def recomment_etf(index_fund_ticker):
    """This tool returns a list of ETFs that are similar (in terms of sector weight distribution) to the index fund ticker provided.
    Args:
        index_fund_tickers: ticker symbol for the primary index fund to compare against
    Returns:
        str: a list of ETFs that are similar to the index fund
    """

    #hardcoded list of candidate ETFs (Similar to VTSAX for demo)
    candidate_etfs = ["VTI","SCHB","ITOT","VOO"]

    def get_sector_weights(ticker):
        """Get the sector weight for a given ticker"""
        t = yf.Ticker(ticker)
        try:
            sector_weights_dict = t.get_funds_data().sector_weightings
            return sector_weights_dict
        except Exception as e:
            print(f"Failed to fetch sector weights for {ticker}:{e}") 
            return {}
    
    #get sector weight dict for index funcd
    base_vector = get_sector_weights(index_fund_ticker)
    if not base_vector:
        print("No sector data available for the index fund")
        return []
    
    sectors = sorted(base_vector.keys())
    base_array = np.array([base_vector.get(s,0.0) for s in sectors]).reshape(1, -1)
    
    results = []
    for etf in candidate_etfs:
        etf_vector = get_sector_weights(etf)
        if not etf_vector:
            continue
        etf_array = np.array([etf_vector.get(s,0.0) for s in sectors]).reshape(1,-1)
        score = cosine_similarity(base_array,etf_array)[0][0]
        results.append((etf,score))

    results.sort(key = lambda x:x[1], reverse = True)
    return results[:2] #return top 2 most similar ETFs

# Kick off server if file is run 
if __name__ == "__main__":
    print("Starting server...")
    mcp.run(transport="stdio")