# Vnstock — Vietnamese Stock Market Data

## Overview

Vnstock is a Python library ecosystem for Vietnamese stock market data and analysis. This skill teaches you how to use vnstock MCP tools correctly.

**Available MCP tools** (prefixed `vnstock__`):

| Tool | What it does |
|---|---|
| `list_all_symbols` | All stock tickers |
| `list_symbols_by_exchange` | Filter by HOSE/HNX/UPCOM |
| `list_symbols_by_group` | Filter by index (VN30, VN100, etc.) |
| `list_symbols_by_industry` | Filter by industry |
| `stock_history` | Historical OHLCV prices |
| `stock_intraday` | Tick-by-tick intraday data |
| `stock_price_depth` | Order book (VCI only) |
| `price_board` | Real-time price board |
| `company_overview` | Company profile & info |
| `company_officers` | Board of directors |
| `company_shareholders` | Major shareholders |
| `company_events` | Dividends, issuances |
| `company_news` | Recent news |
| `income_statement` | Revenue, profit, expenses |
| `balance_sheet` | Assets, liabilities, equity |
| `cash_flow` | Cash flow statement |
| `financial_ratio` | PE, PB, ROE, ROA, Beta |
| **Macro** *(Bronze+)* | | |
| `macro_gdp` | Vietnam GDP growth |
| `macro_cpi` | Consumer Price Index / inflation |
| `macro_exchange_rate` | USD/VND exchange rate |
| `macro_fdi` | Foreign Direct Investment |
| **Commodity** *(Bronze+)* | | |
| `commodity_gold_vn` | Vietnam gold prices (buy/sell) |
| `commodity_oil_crude` | Crude oil prices |
| `commodity_steel_hrc` | HRC steel prices |
| **TopStock** *(Bronze+)* | | |
| `top_gainers` | Top gaining stocks today |
| `top_losers` | Top losing stocks today |
| `top_foreign_buy` | Top foreign net buying |
| `top_foreign_sell` | Top foreign net selling |
| **Fund** *(Bronze+)* | | |
| `fund_listing` | All mutual funds / ETFs |
| `fund_top_holding` | Fund's stock holdings |
| `fund_nav_history` | Fund NAV over time |

## Data Source Selection (CRITICAL)

Two sources available: **KBS** and **VCI**. Default choice matters:

| Use case | Best source | Why |
|---|---|---|
| Listing/symbols | VCI | More data, ICB classification |
| Historical prices | VCI | More intervals, price depth |
| Company info | KBS | 30 columns vs VCI's 10 |
| Financial reports | KBS | Item-based, 90-162 items, bilingual |
| Events | VCI | KBS often returns empty |
| Price board | VCI | 77 columns (detailed) |
| Ratios | KBS | 27 standardized ratios |

**NEVER use TCBS** — it's deprecated.

## Key Constraints

1. **Rate limits**: Free tier = 20 req/min. Add delays between batch requests.
2. **Market hours**: Intraday data only available 9:00-15:00 Vietnam time (UTC+7).
3. **Case-sensitive intervals**: `"M"` = month, `"m"` = minute.
4. **Symbol format**: Always UPPERCASE, 3 chars (e.g., "VCB", "FPT").
5. **Periods**: Financial APIs accept only `"quarter"` or `"year"`.

## Quick Decision Tree

```
User asks about stock price?
  → Current price → price_board
  → Historical → stock_history (interval="1D", length="3M")
  → Intraday ticks → stock_intraday

User asks about a company?
  → Overview → company_overview (source="KBS")
  → Officers → company_officers
  → Events/dividends → company_events (source="VCI")

User asks about financials?
  → Revenue/profit → income_statement
  → Assets/debt → balance_sheet
  → Cash flow → cash_flow
  → Ratios (PE, ROE) → financial_ratio

User asks "find stocks" / screening?
  → By index → list_symbols_by_group (group="VN30")
  → By industry → list_symbols_by_industry
  → All symbols → list_all_symbols
User asks about macro / economy?
  → GDP → macro_gdp
  → Inflation / CPI → macro_cpi
  → Exchange rate → macro_exchange_rate
  → FDI → macro_fdi

User asks about commodity prices?
  → Gold → commodity_gold_vn
  → Oil → commodity_oil_crude
  → Steel → commodity_steel_hrc

User asks "what's hot today?" / market overview?
  → Top gainers → top_gainers
  → Top losers → top_losers
  → Foreign flow → top_foreign_buy + top_foreign_sell

User asks about funds / ETFs?
  → List funds → fund_listing
  → Fund holdings → fund_top_holding
  → Fund performance → fund_nav_history
```

## Related Files

- `data-sources.md` — Detailed KBS vs VCI comparison
- `api-reference.md` — All tool parameters and return formats
- `best-practices.md` — Rate limits, error handling, caching
- `examples.md` — Common multi-tool workflows
