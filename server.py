"""
Vnstock MCP Server
==================
MCP (Model Context Protocol) server wrapping vnstock Python library.
Designed to integrate with GoClaw gateway in managed mode.

Supports: streamable-http transport (default) and stdio transport.

Usage:
  # Streamable HTTP (for Docker / GoClaw managed mode)
  python server.py --transport http --port 8000

  # Stdio (for local testing / GoClaw stdio transport)
  python server.py --transport stdio
"""

import argparse
import json
import logging
import os
import traceback
from datetime import datetime, timedelta

from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("vnstock-mcp")

# ---------------------------------------------------------------------------
# API Key (Bronze+ tier)
# ---------------------------------------------------------------------------
_api_key = os.getenv("VNSTOCK_API_KEY", "")
if _api_key:
    try:
        from vnstock.config import Config
        Config.API_KEY = _api_key
        logger.info("VNSTOCK_API_KEY configured (Bronze+ rate limits active)")
    except Exception as e:
        logger.warning(f"Could not set API key: {e}")

# ---------------------------------------------------------------------------
# MCP Server
# ---------------------------------------------------------------------------
mcp = FastMCP(
    "vnstock",
    host=os.getenv("MCP_HOST", "0.0.0.0"),
    port=int(os.getenv("MCP_PORT", "8000")),
)


# ---------------------------------------------------------------------------
# Helper: DataFrame → dict (MCP-friendly)
# ---------------------------------------------------------------------------
def _df_to_result(df, max_rows: int = 100) -> dict:
    """Convert a pandas DataFrame to a JSON-serialisable dict for MCP responses."""
    if df is None or (hasattr(df, "empty") and df.empty):
        return {"data": [], "total_rows": 0}
    total = len(df)
    truncated = df.head(max_rows)
    return {
        "data": json.loads(truncated.to_json(orient="records", date_format="iso")),
        "total_rows": total,
        "truncated": total > max_rows,
    }


# ===================================================================
# LISTING TOOLS
# ===================================================================

@mcp.tool()
def list_all_symbols(source: str = "VCI") -> dict:
    """List all stock symbols available on Vietnamese exchanges.

    Args:
        source: Data source – "VCI" (recommended) or "KBS".
    """
    from vnstock import Listing

    listing = Listing(source=source)
    df = listing.all_symbols(to_df=True)
    return _df_to_result(df, max_rows=2000)


@mcp.tool()
def list_symbols_by_exchange(exchange: str = "HOSE", source: str = "VCI") -> dict:
    """List stock symbols filtered by exchange.

    Args:
        exchange: Exchange name – "HOSE", "HNX", or "UPCOM".
        source: Data source – "VCI" or "KBS".
    """
    from vnstock import Listing

    listing = Listing(source=source)
    df = listing.symbols_by_exchange(exchange=exchange, to_df=True)
    return _df_to_result(df, max_rows=2000)


@mcp.tool()
def list_symbols_by_group(group: str = "VN30", source: str = "VCI") -> dict:
    """List stock symbols in an index group (e.g. VN30, VN100, VNMID).

    Args:
        group: Index group name – VN30, VN100, VNMID, VNSML, HNX30, etc.
        source: Data source – "VCI" or "KBS".
    """
    from vnstock import Listing

    listing = Listing(source=source)
    df = listing.symbols_by_group(group_name=group, to_df=True)
    return _df_to_result(df)


@mcp.tool()
def list_symbols_by_industry(source: str = "VCI") -> dict:
    """List all stock symbols grouped by industry.

    Args:
        source: Data source – "VCI" or "KBS".
    """
    from vnstock import Listing

    listing = Listing(source=source)
    df = listing.symbols_by_industries(to_df=True)
    return _df_to_result(df, max_rows=2000)


# ===================================================================
# QUOTE / PRICE TOOLS
# ===================================================================

@mcp.tool()
def stock_history(
    symbol: str,
    start: str = "",
    end: str = "",
    interval: str = "1D",
    length: str = "3M",
    source: str = "VCI",
) -> dict:
    """Get historical OHLCV price data for a stock.

    Args:
        symbol: Stock ticker (e.g. "VCB", "FPT", "VCI").
        start: Start date YYYY-MM-DD (optional if length is set).
        end: End date YYYY-MM-DD (defaults to today).
        interval: Time frame – "1m", "5m", "15m", "30m", "1H", "1D", "1W", "1M".
        length: Lookback period – "1W", "1M", "3M", "6M", "1Y", "2Y", or bar count like "100b".
        source: Data source – "VCI" or "KBS".
    """
    from vnstock import Quote

    quote = Quote(symbol=symbol)
    kwargs = {"interval": interval}
    if start:
        kwargs["start"] = start
    if end:
        kwargs["end"] = end
    if not start:
        kwargs["length"] = length
    df = quote.history(**kwargs)
    return _df_to_result(df, max_rows=500)


@mcp.tool()
def stock_intraday(
    symbol: str,
    page_size: int = 100,
    source: str = "VCI",
) -> dict:
    """Get intraday tick-by-tick trading data for a stock.

    Args:
        symbol: Stock ticker (e.g. "VCB").
        page_size: Number of records to return (default 100).
        source: Data source – "VCI" or "KBS".
    """
    from vnstock import Quote

    quote = Quote(symbol=symbol)
    df = quote.intraday(page_size=page_size)
    return _df_to_result(df, max_rows=500)


@mcp.tool()
def stock_price_depth(symbol: str) -> dict:
    """Get price depth (order book) showing buy/sell volume at each price level.
    Only available with VCI data source.

    Args:
        symbol: Stock ticker (e.g. "VCB").
    """
    from vnstock import Quote

    quote = Quote(symbol=symbol)
    df = quote.price_depth()
    return _df_to_result(df)


# ===================================================================
# TRADING TOOLS
# ===================================================================

@mcp.tool()
def price_board(
    symbols: str,
    source: str = "VCI",
) -> dict:
    """Get real-time price board for multiple stocks.

    Args:
        symbols: Comma-separated stock tickers (e.g. "VCB,FPT,ACB").
        source: Data source – "VCI" (77 columns, detailed) or "KBS" (28 columns, stable).
    """
    from vnstock import Trading

    symbols_list = [s.strip().upper() for s in symbols.split(",")]
    trading = Trading(source=source, symbol=symbols_list[0])
    df = trading.price_board(symbols_list=symbols_list)
    return _df_to_result(df)


# ===================================================================
# COMPANY TOOLS
# ===================================================================

@mcp.tool()
def company_overview(symbol: str, source: str = "KBS") -> dict:
    """Get company overview (profile, charter capital, exchange, industry).

    Args:
        symbol: Stock ticker (e.g. "VCB").
        source: Data source – "KBS" (30 columns) or "VCI" (10 columns).
    """
    from vnstock import Company

    company = Company(source=source, symbol=symbol)
    df = company.overview()
    return _df_to_result(df)


@mcp.tool()
def company_officers(symbol: str, source: str = "KBS") -> dict:
    """Get list of company officers (board of directors, CEO, etc.).

    Args:
        symbol: Stock ticker (e.g. "VCB").
        source: Data source – "KBS" or "VCI".
    """
    from vnstock import Company

    company = Company(source=source, symbol=symbol)
    df = company.officers()
    return _df_to_result(df)


@mcp.tool()
def company_shareholders(symbol: str, source: str = "KBS") -> dict:
    """Get major shareholders of a company.

    Args:
        symbol: Stock ticker (e.g. "VCB").
        source: Data source – "KBS" (1 row, largest) or "VCI" (all shareholders).
    """
    from vnstock import Company

    company = Company(source=source, symbol=symbol)
    df = company.shareholders()
    return _df_to_result(df)


@mcp.tool()
def company_events(symbol: str, source: str = "VCI") -> dict:
    """Get company events (dividends, stock issuances, etc.).

    Args:
        symbol: Stock ticker (e.g. "VCB").
        source: Data source – "VCI" recommended (KBS may return empty).
    """
    from vnstock import Company

    company = Company(source=source, symbol=symbol)
    df = company.events()
    return _df_to_result(df)


@mcp.tool()
def company_news(symbol: str, source: str = "KBS") -> dict:
    """Get recent news about a company.

    Args:
        symbol: Stock ticker (e.g. "VCB").
        source: Data source – "KBS" or "VCI".
    """
    from vnstock import Company

    company = Company(source=source, symbol=symbol)
    df = company.news()
    return _df_to_result(df)


# ===================================================================
# FINANCIAL TOOLS
# ===================================================================

@mcp.tool()
def income_statement(
    symbol: str,
    period: str = "quarter",
    source: str = "KBS",
) -> dict:
    """Get income statement (revenue, profit, expenses).

    Args:
        symbol: Stock ticker (e.g. "VCB").
        period: "quarter" or "year".
        source: Data source – "KBS" (item-based, 90 items) or "VCI" (column-based).
    """
    from vnstock import Finance

    finance = Finance(source=source, symbol=symbol)
    df = finance.income_statement(period=period)
    return _df_to_result(df, max_rows=200)


@mcp.tool()
def balance_sheet(
    symbol: str,
    period: str = "quarter",
    source: str = "KBS",
) -> dict:
    """Get balance sheet (assets, liabilities, equity).

    Args:
        symbol: Stock ticker (e.g. "VCB").
        period: "quarter" or "year".
        source: Data source – "KBS" (162 items) or "VCI" (36 columns).
    """
    from vnstock import Finance

    finance = Finance(source=source, symbol=symbol)
    df = finance.balance_sheet(period=period)
    return _df_to_result(df, max_rows=200)


@mcp.tool()
def cash_flow(
    symbol: str,
    period: str = "quarter",
    source: str = "KBS",
) -> dict:
    """Get cash flow statement (operating, investing, financing activities).

    Args:
        symbol: Stock ticker (e.g. "VCB").
        period: "quarter" or "year".
        source: Data source – "KBS" (159 items) or "VCI" (39 columns).
    """
    from vnstock import Finance

    finance = Finance(source=source, symbol=symbol)
    df = finance.cash_flow(period=period)
    return _df_to_result(df, max_rows=200)


@mcp.tool()
def financial_ratio(
    symbol: str,
    period: str = "quarter",
    source: str = "KBS",
) -> dict:
    """Get financial ratios (PE, PB, ROE, ROA, EPS, Beta, etc.).

    Args:
        symbol: Stock ticker (e.g. "VCB").
        period: "quarter" or "year".
        source: Data source – "KBS" (27 ratios) or "VCI" (37+ ratios).
    """
    from vnstock import Finance

    finance = Finance(source=source, symbol=symbol)
    df = finance.ratio(period=period)
    return _df_to_result(df)


# ===================================================================
# MACRO TOOLS (vnstock_data — Bronze+ tier)
# ===================================================================

@mcp.tool()
def macro_gdp(
    start: str = "2020-01",
    end: str = "2025-12",
    period: str = "quarter",
) -> dict:
    """Get Vietnam GDP data (growth rates by sector).

    Args:
        start: Start date YYYY-MM (default "2020-01").
        end: End date YYYY-MM (default "2025-12").
        period: "quarter" or "year".
    """
    from vnstock_data import Macro

    macro = Macro()
    df = macro.gdp(start=start, end=end, period=period)
    return _df_to_result(df, max_rows=200)


@mcp.tool()
def macro_cpi(
    start: str = "2023-01",
    end: str = "2025-12",
    period: str = "month",
) -> dict:
    """Get Vietnam Consumer Price Index (CPI / inflation data).

    Args:
        start: Start date YYYY-MM.
        end: End date YYYY-MM.
        period: "month" or "year".
    """
    from vnstock_data import Macro

    macro = Macro()
    df = macro.cpi(start=start, end=end, period=period)
    return _df_to_result(df, max_rows=200)


@mcp.tool()
def macro_exchange_rate(
    start: str = "2025-01-01",
    end: str = "2025-12-31",
    period: str = "day",
) -> dict:
    """Get USD/VND exchange rate (central rate, interbank, etc.).

    Args:
        start: Start date YYYY-MM-DD (for day) or YYYY-MM (for month/year).
        end: End date (same format as start).
        period: "day", "month", or "year".
    """
    from vnstock_data import Macro

    macro = Macro()
    df = macro.exchange_rate(start=start, end=end, period=period)
    return _df_to_result(df, max_rows=200)


@mcp.tool()
def macro_fdi(
    start: str = "2023-01",
    end: str = "2025-12",
    period: str = "month",
) -> dict:
    """Get Foreign Direct Investment (FDI) data for Vietnam.

    Args:
        start: Start date YYYY-MM.
        end: End date YYYY-MM.
        period: "month" or "year".
    """
    from vnstock_data import Macro

    macro = Macro()
    df = macro.fdi(start=start, end=end, period=period)
    return _df_to_result(df, max_rows=200)


# ===================================================================
# COMMODITY TOOLS (vnstock_data — Bronze+ tier)
# ===================================================================

@mcp.tool()
def commodity_gold_vn(
    start: str = "2025-01-01",
    end: str = "2025-12-31",
) -> dict:
    """Get Vietnam gold prices (buy/sell in VND per chi).

    Args:
        start: Start date YYYY-MM-DD.
        end: End date YYYY-MM-DD.
    """
    from vnstock_data import CommodityPrice

    commodity = CommodityPrice()
    df = commodity.gold_vn(start=start, end=end)
    return _df_to_result(df, max_rows=500)


@mcp.tool()
def commodity_oil_crude(
    start: str = "2025-01-01",
    end: str = "2025-12-31",
) -> dict:
    """Get crude oil prices (OHLCV in USD/barrel).

    Args:
        start: Start date YYYY-MM-DD.
        end: End date YYYY-MM-DD.
    """
    from vnstock_data import CommodityPrice

    commodity = CommodityPrice()
    df = commodity.oil_crude(start=start, end=end)
    return _df_to_result(df, max_rows=500)


@mcp.tool()
def commodity_steel_hrc(
    start: str = "2025-01-01",
    end: str = "2025-12-31",
) -> dict:
    """Get HRC steel prices (OHLCV in USD/ton).

    Args:
        start: Start date YYYY-MM-DD.
        end: End date YYYY-MM-DD.
    """
    from vnstock_data import CommodityPrice

    commodity = CommodityPrice()
    df = commodity.steel_hrc(start=start, end=end)
    return _df_to_result(df, max_rows=500)


# ===================================================================
# INSIGHTS / TOP STOCK TOOLS (vnstock_data — Bronze+ tier)
# ===================================================================

@mcp.tool()
def top_gainers(
    index: str = "VNINDEX",
    limit: int = 10,
) -> dict:
    """Get top gaining stocks today (by % price change).

    Args:
        index: Market index – "VNINDEX", "HNX", or "VN30".
        limit: Number of stocks to return (default 10).
    """
    from vnstock_data import TopStock

    insights = TopStock()
    df = insights.gainer(index=index, limit=limit)
    return _df_to_result(df)


@mcp.tool()
def top_losers(
    index: str = "VNINDEX",
    limit: int = 10,
) -> dict:
    """Get top losing stocks today (by % price change).

    Args:
        index: Market index – "VNINDEX", "HNX", or "VN30".
        limit: Number of stocks to return (default 10).
    """
    from vnstock_data import TopStock

    insights = TopStock()
    df = insights.loser(index=index, limit=limit)
    return _df_to_result(df)


@mcp.tool()
def top_foreign_buy(
    limit: int = 10,
    date: str = "",
) -> dict:
    """Get top stocks with highest foreign net buying value.

    Args:
        limit: Number of stocks to return (default 10).
        date: Trading date YYYY-MM-DD (empty = today).
    """
    from vnstock_data import TopStock

    insights = TopStock()
    kwargs = {"limit": limit}
    if date:
        kwargs["date"] = date
    df = insights.foreign_buy(**kwargs)
    return _df_to_result(df)


@mcp.tool()
def top_foreign_sell(
    limit: int = 10,
    date: str = "",
) -> dict:
    """Get top stocks with highest foreign net selling value.

    Args:
        limit: Number of stocks to return (default 10).
        date: Trading date YYYY-MM-DD (empty = today).
    """
    from vnstock_data import TopStock

    insights = TopStock()
    kwargs = {"limit": limit}
    if date:
        kwargs["date"] = date
    df = insights.foreign_sell(**kwargs)
    return _df_to_result(df)


# ===================================================================
# FUND TOOLS (vnstock_data — Bronze+ tier)
# ===================================================================

@mcp.tool()
def fund_listing(fund_type: str = "") -> dict:
    """List all mutual funds / ETFs available in Vietnam.

    Args:
        fund_type: Filter by type – "STOCK", "BOND", "BALANCED", or empty for all.
    """
    from vnstock_data import Fund

    fund = Fund()
    df = fund.listing(fund_type=fund_type)
    return _df_to_result(df, max_rows=200)


@mcp.tool()
def fund_top_holding(fund_symbol: str) -> dict:
    """Get top stock holdings of a mutual fund.

    Args:
        fund_symbol: Fund short name (e.g. "SSISCA", "DCDS").
    """
    from vnstock_data import Fund

    fund = Fund()
    fund_info = fund.filter(symbol=fund_symbol)
    if fund_info is None or fund_info.empty:
        return {"error": f"Fund '{fund_symbol}' not found", "data": []}
    fund_id = int(fund_info["id"].iloc[0])
    df = fund.top_holding(fundId=fund_id)
    return _df_to_result(df)


@mcp.tool()
def fund_nav_history(fund_symbol: str) -> dict:
    """Get NAV (Net Asset Value) history for a mutual fund.

    Args:
        fund_symbol: Fund short name (e.g. "SSISCA", "DCDS").
    """
    from vnstock_data import Fund

    fund = Fund()
    fund_info = fund.filter(symbol=fund_symbol)
    if fund_info is None or fund_info.empty:
        return {"error": f"Fund '{fund_symbol}' not found", "data": []}
    fund_id = int(fund_info["id"].iloc[0])
    df = fund.nav_report(fundId=fund_id)
    return _df_to_result(df, max_rows=500)


# ===================================================================
# ENTRY POINT
# ===================================================================

def main():
    parser = argparse.ArgumentParser(description="Vnstock MCP Server")
    parser.add_argument(
        "--transport",
        choices=["http", "stdio"],
        default=os.getenv("MCP_TRANSPORT", "http"),
        help="Transport mode: 'http' (streamable-http) or 'stdio'",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("MCP_PORT", "8000")),
        help="HTTP port (only for http transport)",
    )
    parser.add_argument(
        "--host",
        default=os.getenv("MCP_HOST", "0.0.0.0"),
        help="HTTP host (only for http transport)",
    )
    args = parser.parse_args()

    if args.transport == "stdio":
        logger.info("Starting vnstock MCP server (stdio transport)")
        mcp.run(transport="stdio")
    else:
        host = args.host
        port = args.port
        logger.info(f"Starting vnstock MCP server (http transport on {host}:{port})")

        # Update FastMCP settings with CLI args (override env defaults)
        mcp.settings.host = host
        mcp.settings.port = port

        mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()

