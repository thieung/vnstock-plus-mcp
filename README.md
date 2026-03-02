# vnstock-plus-mcp

MCP server cho dữ liệu chứng khoán Việt Nam với **đầy đủ tính năng `vnstock_data` (Bronze+)** — macro, commodity, fund, screening — không chỉ free API như các MCP khác. Tích hợp với [GoClaw](https://github.com/nextlevelbuilder/goclaw) gateway.

## 💡 Tại sao vnstock-plus-mcp?

Các vnstock MCP server khác chỉ cover **vnstock free** (giá, listing, tài chính cơ bản). Server này thêm **12 tools từ `vnstock_data`**:

| Chỉ ở đây | Không có ở MCP khác |
|---|---|
| 🏦 **Macro** | GDP, CPI, tỷ giá, FDI |
| 🟡 **Commodity** | Vàng VN, dầu thô, thép HRC |
| 📈 **TopStock** | Top tăng/giảm, dòng tiền khối ngoại |
| 📊 **Fund** | Quỹ ETF, NAV, holdings |

## ✨ Features

## 🚀 Quick Start

### Local (stdio)

```bash
pip install -r requirements.txt
python server.py --transport stdio
```

### Local (HTTP)

```bash
pip install -r requirements.txt
python server.py --transport http --port 8000
```

### Docker + GoClaw

```bash
# 1. Set API key
echo "VNSTOCK_API_KEY=your-key" >> .env

# 2. Build & start cùng GoClaw stack
docker compose -f docker-compose.yml \
  -f docker-compose.managed.yml \
  -f docker-compose.vnstock-mcp.yml \
  up -d --build

# 3. Đăng ký MCP server với GoClaw
./setup.sh
```

## 🛠️ Tools (30)

| Category | Tools | Tier |
|---|---|---|
| **Listing** | `list_all_symbols`, `list_symbols_by_exchange`, `list_symbols_by_group`, `list_symbols_by_industry` | Free |
| **Quote** | `stock_history`, `stock_intraday`, `stock_price_depth` | Free |
| **Trading** | `price_board` | Free |
| **Company** | `company_overview`, `company_officers`, `company_shareholders`, `company_events`, `company_news` | Free |
| **Finance** | `income_statement`, `balance_sheet`, `cash_flow`, `financial_ratio` | Free |
| **Macro** | `macro_gdp`, `macro_cpi`, `macro_exchange_rate`, `macro_fdi` | Bronze+ |
| **Commodity** | `commodity_gold_vn`, `commodity_oil_crude`, `commodity_steel_hrc` | Bronze+ |
| **TopStock** | `top_gainers`, `top_losers`, `top_foreign_buy`, `top_foreign_sell` | Bronze+ |
| **Fund** | `fund_listing`, `fund_top_holding`, `fund_nav_history` | Bronze+ |

## 📁 Project Structure

```
├── server.py                       # MCP server (30 tools)
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Multi-stage Docker build
├── docker-compose.vnstock-mcp.yml  # Docker Compose overlay
├── setup.sh                        # GoClaw registration script
├── skills/vnstock/                 # GoClaw SKILL knowledge base
│   ├── SKILL.md                    # Entry point + decision tree
│   ├── data-sources.md             # KBS vs VCI comparison
│   ├── api-reference.md            # All tool parameters
│   ├── best-practices.md           # Rate limits, error handling
│   └── examples.md                 # Multi-tool workflows
└── docs/                           # vnstock API documentation
```

## ⚙️ Configuration

| Env Variable | Default | Description |
|---|---|---|
| `MCP_TRANSPORT` | `http` | Transport: `http` or `stdio` |
| `MCP_PORT` | `8000` | HTTP port |
| `MCP_HOST` | `0.0.0.0` | HTTP host |
| `VNSTOCK_API_KEY` | *(empty)* | API key for Bronze+ rate limits |
| `LOG_LEVEL` | `INFO` | Logging level |

## 📊 Rate Limits

| Tier | Limit | API Key Required |
|---|---|---|
| Free | 20 req/min | No |
| Free + Key | 60 req/min | Yes |
| Bronze | 180 req/min | Yes |
| Silver | 300 req/min | Yes |
| Golden | 600 req/min | Yes |

## 📚 References

- [vnstock](https://github.com/thinh-vu/vnstock) — Vietnamese stock market data library
- [vnstock-agent-guide](https://github.com/vnstock-hq/vnstock-agent-guide) — AI agent documentation
- [GoClaw](https://github.com/nextlevelbuilder/goclaw) — Multi-agent AI gateway
- [MCP Protocol](https://modelcontextprotocol.io/) — Model Context Protocol spec

## License

MIT
