from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel
import yfinance as yf
from typing import Dict, List, Optional

class StockAnalysis(BaseModel):
    """
    A class that represents the comprehensive stock data for a given stock symbol.
    """
    ticker: str
    current_price: float
    opening_price: float
    day_high: float
    day_low: float
    market_cap: str
    pe_ratio: float
    dividend_yield: float
    fifty_two_week_range: str
    recent_news: List[str]


load_dotenv()
mcp = FastMCP("Stock Analysis Server")

@mcp.tool(
    name="check_stock_price",
    description="Get the current price of a stock symbol",
)
def check_stock_price(stock_symbol: str) -> str:
    """Get the current price of a stock symbol"""
    ticker = yf.Ticker(stock_symbol)
    hist = ticker.history(period="1d", interval="1d")
    current_price = hist['Close'].iloc[-1] if not hist.empty else 0.0
    print(f"Current price of {stock_symbol} today: ${current_price}")
    return f"${current_price:.2f}"

@mcp.tool(
    description="Get comprehensive stock data including price, financial metrics, and recent news.",
)
def get_comprehensive_stock_data(stock_symbol: str) -> StockAnalysis:
    """
    Get comprehensive stock data including price, financial metrics, and recent news.
    
    Args:
        stock_symbol: The stock ticker symbol (e.g., 'AAPL', 'MSFT')
    
    Returns:
        Comprehensive stock analysis including current price, financial metrics, and news
    """
    try:
        # Initialize ticker object
        ticker = yf.Ticker(stock_symbol)
        
        # Get current day's data
        hist = ticker.history(period="1d", interval="1d")
        
        # Get company info
        info = ticker.info
        
        # Get recent news
        news = ticker.news
        
        # Extract key data points
        current_price = hist['Close'].iloc[-1] if not hist.empty else 0.0
        opening_price = hist['Open'].iloc[0] if not hist.empty else 0.0
        day_high = hist['High'].iloc[0] if not hist.empty else 0.0
        day_low = hist['Low'].iloc[0] if not hist.empty else 0.0
        
        # Financial metrics
        market_cap = info.get('marketCap', 0)
        if market_cap:
            if market_cap >= 1e12:
                market_cap_str = f"{market_cap/1e12:.1f}T"
            elif market_cap >= 1e9:
                market_cap_str = f"{market_cap/1e9:.1f}B"
            elif market_cap >= 1e6:
                market_cap_str = f"{market_cap/1e6:.1f}M"
            else:
                market_cap_str = f"{market_cap:,.0f}"
        else:
            market_cap_str = "N/A"
        
        pe_ratio = info.get('trailingPE', 0.0)
        dividend_yield = info.get('dividendYield', 0.0)
        if dividend_yield:
            dividend_yield = dividend_yield * 100  # Convert to percentage
        
        # 52-week range
        fifty_two_week_low = info.get('fiftyTwoWeekLow', 0)
        fifty_two_week_high = info.get('fiftyTwoWeekHigh', 0)
        fifty_two_week_range = f"{fifty_two_week_low:.1f} – {fifty_two_week_high:.1f}" if fifty_two_week_low and fifty_two_week_high else "N/A"
        
        # Recent news headlines (limit to 3)
        recent_news = []
        if news:
            for article in news[:3]:
                title = article.get('title', '')
                if title:
                    recent_news.append(title)
        
        return StockAnalysis(
            ticker=stock_symbol,
            current_price=current_price,
            opening_price=opening_price,
            day_high=day_high,
            day_low=day_low,
            market_cap=market_cap_str,
            pe_ratio=pe_ratio,
            dividend_yield=dividend_yield,
            fifty_two_week_range=fifty_two_week_range,
            recent_news=recent_news,
        )
        
    except Exception as e:
        # Return error structure
        return StockAnalysis(
            ticker=stock_symbol,
            current_price=0.0,
            opening_price=0.0,
            day_high=0.0,
            day_low=0.0,
            market_cap="Error",
            pe_ratio=0.0,
            dividend_yield=0.0,
            fifty_two_week_range="Error",
            recent_news=["Unable to fetch news"],
            prompt=f"Error retrieving data for {stock_symbol}: {str(e)}"
        )

if __name__ == "__main__":
    mcp.run(transport="streamable-http")