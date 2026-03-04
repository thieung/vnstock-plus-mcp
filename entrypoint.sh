#!/bin/sh
# =============================================================================
# entrypoint.sh — vnstock MCP server Docker entrypoint
#
# 1. If VNSTOCK_API_KEY is set and vnstock_data is NOT installed,
#    install it directly via API (bypasses complex CLI installer).
# 2. Start the MCP server.
# =============================================================================
set -e

# --- Try installing vnstock_data if API key is provided ---
if [ -n "$VNSTOCK_API_KEY" ]; then
    if python -c "import vnstock_data" 2>/dev/null; then
        echo "✅ vnstock_data already installed"
    else
        echo "📦 vnstock_data not found. Installing via API (Bronze+ tier)..."

        # Use our lightweight installer (bypasses CLI installer venv issues)
        set +e
        python /app/install_vnstock_data.py 2>&1
        INSTALL_EXIT=$?
        set -e

        if [ $INSTALL_EXIT -ne 0 ]; then
            echo "⚠️  vnstock_data installation failed (exit: $INSTALL_EXIT)."
            echo "   Continuing with free-tier tools only."
        fi
    fi
else
    echo "ℹ️  No VNSTOCK_API_KEY set. Running with free-tier tools only (17 tools)."
    echo "   Set VNSTOCK_API_KEY to enable Bronze+ tools (31 tools total)."
fi

# --- Start MCP server ---
echo "🚀 Starting vnstock MCP server..."
exec python server.py "$@"
