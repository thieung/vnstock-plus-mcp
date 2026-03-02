# Best Practices — Rate Limits, Errors & Caching

## Rate Limits

| Tier | Limit | Interval |
|---|---|---|
| Free (no key) | 20 req/min | ~3s between requests |
| Free (with key) | 60 req/min | ~1s between requests |
| **Bronze** | **180 req/min** | **~0.3s** |
| Silver | 300 req/min | ~0.2s |
| Golden | 600 req/min | ~0.1s |

> **Current tier: Bronze (180 req/min)**

### When batch-requesting:
- **Do NOT** loop through 100+ symbols without delay
- Process VN30 (30 stocks): ~90 seconds at free tier
- Use `price_board` with comma-separated symbols instead of individual `stock_history` calls
- Cache listing data (symbols rarely change)

## Error Handling

### Common errors and fixes

| Error | Cause | Fix |
|---|---|---|
| Empty DataFrame | No data for symbol/period | Try different source (KBS↔VCI) |
| ValueError: invalid symbol | Typo or delisted stock | Check with `list_all_symbols` first |
| HTTPError 403 | IP blocked (cloud env) | Use proxy or wait |
| HTTPError 429 | Rate limit hit | Wait 60s, reduce request frequency |
| NotImplementedError | Method not available on source | Switch source (e.g., ICB → VCI only) |
| RetryError | Network timeout | Retry after 5s |

### Defensive patterns

1. **Always validate symbol first** before multiple API calls:
   - Call `list_all_symbols` and check if symbol exists
   
2. **Fallback between sources**:
   - If KBS returns empty → try VCI
   - Especially for: `company_events`, `company_shareholders`

3. **Check DataFrame before processing**:
   - Tool may return `{"data": [], "total_rows": 0}` 
   - Always check `total_rows > 0` before analyzing

## Response Formatting

### For price data:
- Format prices with commas: 84,500 VND
- Show % change with +/- sign: +1.18%
- Include date/time context

### For financial data (KBS format):
- Data is item-based (rows = items, columns = periods)
- Key item_ids: `revenue`, `net_profit`, `total_assets`, `owner_equity`
- Period format: `"2025-Q3"` (quarter), `"2025"` (year)

### For tables:
- Limit to 10-20 rows for readability
- Highlight key metrics (bold or emoji)
- Always mention the data source used

## Performance Tips

1. **Use `price_board`** for current prices of multiple stocks (1 request)
2. **Use `list_symbols_by_group`** instead of filtering `list_all_symbols`
3. **Financial data**: Fetch once, extract multiple metrics from same response
4. **Don't fetch intraday** outside market hours (9:00-15:00 UTC+7)

## vnstock_data Specific Notes

1. **Macro data source**: Only MBK (MayBank) — no source parameter needed
2. **Commodity data source**: Only SPL — no source parameter needed
3. **TopStock data source**: Only VND — no source parameter needed
4. **Fund data source**: Only Fmarket — no source parameter needed
5. **Date formats differ**: Macro uses YYYY-MM, Commodity uses YYYY-MM-DD
6. **Fund lookup**: Always use `fund_top_holding(fund_symbol="SSISCA")` — the tool handles ID lookup internally
