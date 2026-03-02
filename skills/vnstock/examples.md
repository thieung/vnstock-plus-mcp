# Examples — Common Multi-Tool Workflows

## 1. "Giá VCB hiện tại bao nhiêu?"

**Tools**: `price_board`

```
→ price_board(symbols="VCB")
→ Report: reference_price, price_change, percent_change
```

## 2. "Phân tích cổ phiếu FPT"

**Tools**: `company_overview` → `stock_history` → `financial_ratio`

```
Step 1: company_overview(symbol="FPT", source="KBS")
  → Get: business model, charter capital, exchange, employees

Step 2: stock_history(symbol="FPT", length="6M", interval="1D")
  → Get: 6-month price trend, high/low range

Step 3: financial_ratio(symbol="FPT", period="quarter", source="KBS")
  → Get: PE, PB, ROE, ROA, Beta

→ Combine into analysis report
```

## 3. "Top cổ phiếu VN30 tăng mạnh nhất hôm nay"

**Tools**: `list_symbols_by_group` → `price_board`

```
Step 1: list_symbols_by_group(group="VN30")
  → Get: list of 30 symbols

Step 2: price_board(symbols="ACB,BCM,BID,CTG,...")  
  → Pass all 30 symbols comma-separated (1 request!)

→ Sort by percent_change DESC, show top 5
```

## 4. "So sánh VCB vs CTG vs BID"

**Tools**: `price_board` → `financial_ratio` (×3)

```
Step 1: price_board(symbols="VCB,CTG,BID")
  → Current prices side by side

Step 2: financial_ratio(symbol="VCB") 
Step 3: financial_ratio(symbol="CTG")
Step 4: financial_ratio(symbol="BID")
  → Compare PE, PB, ROE

→ Comparison table
```

## 5. "Lịch sử chia cổ tức của VNM"

**Tools**: `company_events`

```
→ company_events(symbol="VNM", source="VCI")
  ⚠️ Always use VCI for events (KBS often empty)
→ Filter by event_list_code = "DIV" for dividends
→ Show: event_title, ratio, record_date, exright_date
```

## 6. "Báo cáo tài chính ACB 4 quý gần nhất"

**Tools**: `income_statement` → `balance_sheet` → `financial_ratio`

```
Step 1: income_statement(symbol="ACB", period="quarter")
  → Key items: revenue, net_profit (filter by item_id)

Step 2: balance_sheet(symbol="ACB", period="quarter")
  → Key items: total_assets, owner_equity, liabilities

Step 3: financial_ratio(symbol="ACB", period="quarter")
  → Key ratios: ROE, ROA, PE, PB

→ Quarterly trend summary table
```

## 7. "Tìm cổ phiếu ngành ngân hàng"

**Tools**: `list_symbols_by_industry` → `price_board`

```
Step 1: list_symbols_by_industry(source="VCI")
  → Filter results where industry contains "Ngân hàng"

Step 2: price_board(symbols="VCB,CTG,BID,ACB,MBB,...")
  → Get current prices for all banking stocks

→ Banking sector overview table
```

## 8. "VCB có bao nhiêu cổ đông lớn?"

**Tools**: `company_shareholders`

```
→ company_shareholders(symbol="VCB", source="VCI")
  ⚠️ Use VCI for full list (KBS only returns top 1)
→ Show: shareholder name, shares_owned, ownership_percentage
```

## 9. "Hôm nay thị trường thế nào?" (Bronze+)

**Tools**: `top_gainers` → `top_losers` → `top_foreign_buy`

```
Step 1: top_gainers(index="VNINDEX", limit=5)
  → Top 5 tăng mạnh nhất

Step 2: top_losers(index="VNINDEX", limit=5)
  → Top 5 giảm mạnh nhất

Step 3: top_foreign_buy(limit=5)
  → Top 5 NĐTNN mua ròng

→ Tổng hợp thành market overview
```

## 10. "GDP Việt Nam quý gần nhất?" (Bronze+)

**Tools**: `macro_gdp`

```
→ macro_gdp(start="2024-01", end="2025-12", period="quarter")
→ Filter name == "Tổng GDP"
→ Report: growth rate, sector breakdown
```

## 11. "Giá vàng hôm nay?" (Bronze+)

**Tools**: `commodity_gold_vn`

```
→ commodity_gold_vn(start="2025-01-01", end="2025-12-31")
→ Report latest row: buy price, sell price (VND/chỉ)
```

## 12. "Quỹ SSISCA đầu tư vào CP gì?" (Bronze+)

**Tools**: `fund_top_holding`

```
→ fund_top_holding(fund_symbol="SSISCA")
→ Show: stock_code, industry, net_asset_percent
```

## Anti-patterns (DON'T DO)

❌ **Don't** call `stock_history` in a loop for 30+ stocks
  → Use `price_board` for current prices instead

❌ **Don't** use `source="TCBS"` — it's deprecated

❌ **Don't** call `stock_intraday` outside trading hours (9:00-15:00 UTC+7)

❌ **Don't** assume `company_events` works with KBS — always use VCI

❌ **Don't** confuse `interval="M"` (month) with `"m"` (minute)

❌ **Don't** call macro/commodity tools without vnstock_data installed (Bronze+ only)

❌ **Don't** use `fund_top_holding(fund_symbol="11")` — pass the **name** not the ID
