# Data Sources — KBS vs VCI

## Summary

| Source | Stability | Detail | Best for |
|---|---|---|---|
| **KBS** | ⭐⭐⭐ High | Standard | Company info, financials, ratios |
| **VCI** | ⭐⭐ Good | Very detailed | Listing, prices, events, trading |

## Per-API Comparison

### Listing
| Method | KBS | VCI | Winner |
|---|---|---|---|
| `all_symbols` | 1565 symbols, 2 cols | 1733 symbols, 2 cols | VCI (more) |
| `symbols_by_exchange` | 6 cols | 7 cols + ICB | VCI |
| `symbols_by_industries` | 3 cols | 10 cols | VCI |
| `symbols_by_group` | ✅ | ✅ | Either |
| `industries_icb` | ❌ NotImplemented | ✅ | VCI only |
| `all_etf` | ✅ | ❌ | KBS only |

### Quote / Price
| Method | KBS | VCI | Winner |
|---|---|---|---|
| `history` | ✅ OHLCV | ✅ OHLCV | Either |
| `intraday` | ✅ get_all option | ✅ last_time filter | Either |
| `price_depth` | ❌ | ✅ | VCI only |

### Company
| Method | KBS | VCI | Winner |
|---|---|---|---|
| `overview` | 30 cols | 10 cols | KBS (richer) |
| `shareholders` | 1 row (top only) | All shareholders | VCI (more data) |
| `officers` | ✅ | ✅ + filter_by | VCI |
| `events` | Often empty ⚠️ | 32+ events | VCI |
| `news` | ✅ | ✅ | Either |
| `ownership` | ✅ | ❌ | KBS only |
| `capital_history` | ✅ | ❌ | KBS only |
| `insider_trading` | ✅ | ❌ | KBS only |
| `trading_stats` | ❌ | ✅ | VCI only |
| `ratio_summary` | ❌ | ✅ | VCI only |

### Financial
| Method | KBS | VCI | Winner |
|---|---|---|---|
| `income_statement` | 90 items, Vi+En | 25+ cols, En | KBS (detailed) |
| `balance_sheet` | 162 items | 36 cols | KBS |
| `cash_flow` | 159 items | 39 cols | KBS |
| `ratio` | 27 ratios | 37+ ratios | VCI (more ratios) |

### Trading
| Method | KBS | VCI | Winner |
|---|---|---|---|
| `price_board` | 28 cols | 77 cols | VCI (detailed) |

## Fallback Strategy

When KBS returns empty data, fallback to VCI:
- `company_events` → almost always need VCI
- `shareholders` → VCI for full list, KBS only top 1

When VCI fails (network/timeout), fallback to KBS:
- Most company and financial methods work on KBS

## vnstock_data Exclusive Sources (Bronze+ tier)

These tools have **fixed data sources** — no `source` parameter:

| Tool category | Source | Data source |
|---|---|---|
| **Macro** | MBK (MayBank) | GDP, CPI, FDI, exchange rate |
| **Commodity** | SPL | Gold, oil, steel, agriculture |
| **TopStock** | VND | Gainers, losers, foreign flow |
| **Fund** | Fmarket | ETFs, mutual funds |

