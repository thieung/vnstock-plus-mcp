#!/usr/bin/env bash
# =============================================================================
# setup.sh — Register vnstock MCP server with GoClaw (managed mode)
#
# Prerequisites:
#   - GoClaw running in managed mode
#   - GOCLAW_GATEWAY_TOKEN set in environment or .env
#   - vnstock-mcp container running and healthy
#
# Usage:
#   ./setup.sh                          # Use defaults (localhost:18790)
#   GOCLAW_HOST=my-vps.com ./setup.sh   # Custom GoClaw host
# =============================================================================

set -euo pipefail

# --- Configuration ---
GOCLAW_BASE="${GOCLAW_HOST:-http://localhost:18790}"

# Load .env if present
if [[ -f .env ]]; then
    # shellcheck disable=SC1091
    set -a && source .env && set +a
fi

if [[ -z "${GOCLAW_GATEWAY_TOKEN:-}" ]]; then
    echo "❌ Error: GOCLAW_GATEWAY_TOKEN is not set."
    echo "   Set it in .env or export it before running this script."
    exit 1
fi

echo "🔗 Registering vnstock MCP server with GoClaw at ${GOCLAW_BASE}..."

# --- Step 1: Register MCP server ---
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "${GOCLAW_BASE}/v1/mcp/servers" \
    -H "Authorization: Bearer ${GOCLAW_GATEWAY_TOKEN}" \
    -H "Content-Type: application/json" \
    -d '{
        "name": "vnstock",
        "transport": "streamable-http",
        "url": "http://vnstock-mcp:8000/mcp",
        "enabled": true,
        "tool_prefix": "vnstock"
    }')

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [[ "$HTTP_CODE" == "200" || "$HTTP_CODE" == "201" ]]; then
    MCP_ID=$(echo "$BODY" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', 'unknown'))" 2>/dev/null || echo "unknown")
    echo "✅ MCP server registered successfully! ID: ${MCP_ID}"
    echo ""
    echo "📝 Next steps:"
    echo "   1. Grant access to an agent:"
    echo "      curl -X POST ${GOCLAW_BASE}/v1/mcp/servers/${MCP_ID}/grants/agent \\"
    echo '        -H "Authorization: Bearer $GOCLAW_GATEWAY_TOKEN" \\'
    echo '        -H "Content-Type: application/json" \\'
    echo "        -d '{\"agent_id\": \"YOUR_AGENT_ID\"}'"
    echo ""
    echo "   2. Or use the GoClaw Web Dashboard to manage grants."
elif [[ "$HTTP_CODE" == "409" ]]; then
    echo "⚠️  MCP server 'vnstock' already registered. Skipping."
    echo "    Use the API or Web Dashboard to update it if needed."
else
    echo "❌ Failed to register MCP server (HTTP ${HTTP_CODE}):"
    echo "$BODY"
    exit 1
fi

echo ""
echo "🎉 Setup complete! Your GoClaw agents can now use vnstock tools."
echo "   Available tools (with 'vnstock__' prefix):"
echo "   - vnstock__list_all_symbols"
echo "   - vnstock__list_symbols_by_group"
echo "   - vnstock__stock_history"
echo "   - vnstock__stock_intraday"
echo "   - vnstock__price_board"
echo "   - vnstock__company_overview"
echo "   - vnstock__company_officers"
echo "   - vnstock__income_statement"
echo "   - vnstock__balance_sheet"
echo "   - vnstock__financial_ratio"
echo "   - ... and more"
