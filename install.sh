#!/bin/bash
# ============================================================
# Databricks SQL MCP Server - Installer for Mac/Linux
# ============================================================

set -e

echo ""
echo "=============================================="
echo "  Databricks SQL MCP Server - Quick Install"
echo "=============================================="
echo ""
echo "This script will configure Claude Desktop to"
echo "use the Databricks SQL MCP server via Docker."
echo ""

# Check prerequisites
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed or not in PATH."
    echo "Please install Docker first: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v claude &> /dev/null; then
    echo "ERROR: Claude CLI is not installed or not in PATH."
    echo "Please install Claude CLI first: https://docs.anthropic.com/en/docs/claude-code"
    exit 1
fi

echo "-- Prerequisites OK (Docker + Claude CLI found)"
echo ""

# Prompt for credentials
echo "Enter your Databricks credentials."
echo "(See README for help finding these values)"
echo ""

read -p "Databricks Host URL (e.g. https://adb-123.azuredatabricks.net): " DATABRICKS_HOST
if [ -z "$DATABRICKS_HOST" ]; then
    echo "ERROR: Databricks Host URL is required."
    exit 1
fi

read -sp "Databricks Personal Access Token (starts with dapi...): " DATABRICKS_TOKEN
echo
if [ -z "$DATABRICKS_TOKEN" ]; then
    echo "ERROR: Databricks Token is required."
    exit 1
fi

read -p "SQL Warehouse ID: " DATABRICKS_WAREHOUSE_ID
if [ -z "$DATABRICKS_WAREHOUSE_ID" ]; then
    echo "ERROR: SQL Warehouse ID is required."
    exit 1
fi

echo ""
echo "-- Pulling Docker image..."
docker pull bkeeleygib/databricks-sql-mcp:latest

echo ""
echo "-- Configuring Claude Desktop..."

# Build the JSON config
CONFIG=$(cat <<EOF
{
  "command": "docker",
  "args": [
    "run",
    "-i",
    "--rm",
    "-e", "DATABRICKS_HOST=${DATABRICKS_HOST}",
    "-e", "DATABRICKS_TOKEN=${DATABRICKS_TOKEN}",
    "-e", "DATABRICKS_WAREHOUSE_ID=${DATABRICKS_WAREHOUSE_ID}",
    "bkeeleygib/databricks-sql-mcp:latest"
  ]
}
EOF
)

claude mcp add-json databricks-sql "$CONFIG"

echo ""
echo "=============================================="
echo "  Installation Complete!"
echo "=============================================="
echo ""
echo "The 'databricks-sql' MCP server has been added"
echo "to your Claude Desktop configuration."
echo ""
echo "Next steps:"
echo "  1. Restart Claude Desktop completely"
echo "  2. Ask Claude: 'List all catalogs in my Unity Catalog'"
echo ""
echo "To verify your config:"
echo "  cat ~/Library/Application\ Support/Claude/claude_desktop_config.json"
echo ""
