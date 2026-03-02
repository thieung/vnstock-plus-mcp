# API Reference — Quick Parameter Guide

## Listing Tools

### list_all_symbols
```
source: "VCI" | "KBS"   (default: "VCI")
```
Returns: `symbol`, `organ_name`

### list_symbols_by_exchange
```
exchange: "HOSE" | "HNX" | "UPCOM"   (required)
source:   "VCI" | "KBS"              (default: "VCI")
```

### list_symbols_by_group
```
group:  "VN30" | "VN100" | "VNMID" | "VNSML" | "HNX30" | "VNALL" | ...
source: "VCI" | "KBS"
```
Available groups: VN30, VN100, VNMID, VNSML, VNALL, VNSI, VNIT, VNIND, VNCONS, VNCOND, VNHEAL, VNENE, VNUTI, VNREAL, VNFIN, VNMAT, VNDIAMOND, VNFINLEAD, VNFINSELECT, VNX50, VNXALL

### list_symbols_by_industry
```
source: "VCI" | "KBS"
```

---

## Quote / Price Tools

### stock_history
```
symbol:   "VCB"              (required, uppercase)
start:    "2024-01-01"       (optional, YYYY-MM-DD)
end:      "2024-12-31"       (optional, defaults to today)
interval: "1D"               (default)
length:   "3M"               (default, used when start is empty)
source:   "VCI" | "KBS"
```

**interval values** (case-sensitive!):
- Minutes: `"1m"`, `"5m"`, `"15m"`, `"30m"`
- Hours: `"1H"`
- Daily+: `"1D"`, `"1W"`, `"1M"`

**length values**:
- Period: `"1W"`, `"1M"`, `"3M"`, `"6M"`, `"1Y"`, `"2Y"`, `"5Y"`
- Custom: `"10D"`, `"3W"`, `"1Q"`
- Days: `100` or `"150"`
- Bars: `"100b"`, `"50b"`

### stock_intraday
```
symbol:    "VCB"    (required)
page_size: 100      (default, number of ticks)
source:    "VCI" | "KBS"
```
Returns: `time`, `price`, `volume`, `match_type`, `id`

### stock_price_depth
```
symbol: "VCB"   (required)
```
⚠️ VCI only! Returns: `price`, `volume`, `buy_volume`, `sell_volume`

---

## Trading Tools

### price_board
```
symbols: "VCB,FPT,ACB"   (required, comma-separated)
source:  "VCI" | "KBS"
```
KBS returns 28 cols, VCI returns 77 cols.

---

## Company Tools

### company_overview
```
symbol: "VCB"              (required)
source: "KBS" | "VCI"      (default: "KBS")
```

### company_officers
```
symbol: "VCB"
source: "KBS" | "VCI"      (default: "KBS")
```

### company_shareholders
```
symbol: "VCB"
source: "KBS" | "VCI"      (default: "KBS")
```
⚠️ KBS returns only top 1 shareholder. Use VCI for full list.

### company_events
```
symbol: "VCB"
source: "KBS" | "VCI"      (default: "VCI")
```
⚠️ KBS often returns empty. Always default to VCI.

### company_news
```
symbol: "VCB"
source: "KBS" | "VCI"      (default: "KBS")
```

---

## Financial Tools

All financial tools share the same params:
```
symbol: "VCB"              (required)
period: "quarter" | "year"  (default: "quarter")
source: "KBS" | "VCI"      (default: "KBS")
```

### income_statement
KBS: 90 items (rows) with `item`, `item_id`, period columns
VCI: 25+ columns, each row = 1 period

### balance_sheet
KBS: 162 items | VCI: 36 columns

### cash_flow
KBS: 159 items | VCI: 39 columns

### financial_ratio
KBS: 27 ratios (PE, PB, ROE, ROA, Beta, EPS, etc.)
VCI: 37+ ratios

---

## Macro Tools (Bronze+ tier)

All macro tools use `vnstock_data.Macro`.

### macro_gdp
```
start:  "2020-01"   (YYYY-MM)
end:    "2025-12"   (YYYY-MM)
period: "quarter" | "year"
```
Returns: `last_updated`, `group_name`, `name`, `value`, `unit`, `source`, `report_type`

### macro_cpi
```
start:  "2023-01"   (YYYY-MM)
end:    "2025-12"   (YYYY-MM)
period: "month" | "year"
```

### macro_exchange_rate
```
start:  "2025-01-01"  (YYYY-MM-DD for day, YYYY-MM for month)
end:    "2025-12-31"
period: "day" | "month" | "year"
```

### macro_fdi
```
start:  "2023-01"   (YYYY-MM)
end:    "2025-12"   (YYYY-MM)
period: "month" | "year"
```

---

## Commodity Tools (Bronze+ tier)

All commodity tools use `vnstock_data.CommodityPrice`.

### commodity_gold_vn
```
start: "2025-01-01"  (YYYY-MM-DD)
end:   "2025-12-31"  (YYYY-MM-DD)
```
Returns: `buy`, `sell` (VND per chi)

### commodity_oil_crude
```
start: "2025-01-01"
end:   "2025-12-31"
```
Returns: `open`, `high`, `low`, `close`, `volume` (USD/barrel)

### commodity_steel_hrc
```
start: "2025-01-01"
end:   "2025-12-31"
```
Returns: OHLCV (USD/ton)

---

## TopStock / Insights Tools (Bronze+ tier)

### top_gainers / top_losers
```
index: "VNINDEX" | "HNX" | "VN30"
limit: 10   (default)
```
Returns 15 cols: `symbol`, `last_price`, `price_change_pct_1d`, `volume_spike_20d_pct`, etc.

### top_foreign_buy / top_foreign_sell
```
limit: 10
date:  ""      (empty = today, or YYYY-MM-DD)
```
Returns: `symbol`, `date`, `net_value` (VND)

---

## Fund Tools (Bronze+ tier)

### fund_listing
```
fund_type: "" | "STOCK" | "BOND" | "BALANCED"
```
Returns 21 cols: `short_name`, `nav`, `management_fee`, `nav_change_*`, etc.

### fund_top_holding
```
fund_symbol: "SSISCA"   (required, fund short name)
```
Returns: `stock_code`, `industry`, `net_asset_percent`

### fund_nav_history
```
fund_symbol: "SSISCA"   (required)
```
Returns: `date`, `nav_per_unit`
