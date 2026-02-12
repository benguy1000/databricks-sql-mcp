# Databricks SQL MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-bkeeleygib%2Fdatabricks--sql--mcp-blue)](https://hub.docker.com/r/bkeeleygib/databricks-sql-mcp)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server that lets AI assistants like Claude execute SQL queries on Databricks. Claude launches the server as a Docker container and communicates over stdin/stdout using the MCP stdio transport.

## Features

**Core Tools:**
- `execute_sql` - Run any SQL query against a Databricks SQL Warehouse
- `list_databases` - List databases/schemas in the default catalog
- `list_tables` - List tables in a specific database
- `describe_table` - Show column names, types, and comments for a table

**Unity Catalog Tools:**
- `list_catalogs` - List all catalogs in the Unity Catalog metastore
- `list_schemas` - List schemas within a specific catalog
- `list_tables_full` - List tables using full 3-part naming (`catalog.schema.table`)
- `describe_table_full` - Describe a table using its full catalog path

## Unity Catalog Hierarchy

```
CATALOG (e.g., analytics)
  └── SCHEMA/DATABASE (e.g., silver)
      └── TABLE (e.g., customers)
```

**Fully qualified name:** `catalog.schema.table` (e.g., `analytics.silver.customers`)

## Prerequisites

- **Docker** installed and running
- **Databricks workspace** access with a SQL Warehouse
- **Databricks personal access token**
- **Claude Desktop** or **Claude Code** (CLI)

## Getting Your Databricks Credentials

### 1. Databricks Host URL

Your workspace URL. The format depends on your cloud provider:

| Cloud | Example URL |
|-------|------------|
| Azure | `https://adb-1234567890.azuredatabricks.net` |
| AWS   | `https://my-workspace.cloud.databricks.com` |
| GCP   | `https://my-workspace.gcp.databricks.com` |

### 2. Personal Access Token

1. Open your Databricks workspace
2. Click your username (top-right)
3. Go to **User Settings** > **Developer** > **Access tokens**
4. Click **Generate new token**
5. Copy the token (starts with `dapi...`)

### 3. SQL Warehouse ID

1. Go to **SQL Warehouses** in Databricks
2. Click on a warehouse
3. Copy the warehouse ID from the URL: `/sql/warehouses/<this-id>`

## Quick Install (Recommended)

The install scripts pull the Docker image, prompt for your Databricks credentials, and register the MCP server with Claude using the Claude Code CLI.

### Mac / Linux

```bash
curl -fsSL https://raw.githubusercontent.com/benguy1000/databricks-sql-mcp/master/install.sh | bash
```

Or clone the repo first:

```bash
git clone https://github.com/benguy1000/databricks-sql-mcp.git
cd databricks-sql-mcp
chmod +x install.sh
./install.sh
```

### Windows (PowerShell)

```powershell
git clone https://github.com/benguy1000/databricks-sql-mcp.git
cd databricks-sql-mcp
.\install.bat
```

After running the installer, restart Claude Desktop (or start a new Claude Code session) and you're ready to go.

---

## Manual Installation

If you prefer to set things up manually, or if the quick install doesn't work for your setup, follow the steps below.

### Running with Docker

#### Pull the Image from Docker Hub

```bash
docker pull bkeeleygib/databricks-sql-mcp:latest
```

Or build it yourself:

```bash
docker build -t bkeeleygib/databricks-sql-mcp .
```

#### Run with Environment Variables

The `-i` flag is required -- MCP uses stdin/stdout for communication between Claude and the server.

```bash
docker run -i --rm \
  -e DATABRICKS_HOST="https://your-workspace.azuredatabricks.net" \
  -e DATABRICKS_TOKEN="dapi1234567890abcdef" \
  -e DATABRICKS_WAREHOUSE_ID="abc123def456" \
  bkeeleygib/databricks-sql-mcp:latest
```

#### Run with .env File

Create a `.env` file with your credentials (see [.env.example](.env.example)):

```
DATABRICKS_HOST=https://your-workspace.azuredatabricks.net
DATABRICKS_TOKEN=dapi1234567890abcdef
DATABRICKS_WAREHOUSE_ID=abc123def456
```

Then run:

```bash
docker run -i --rm --env-file .env bkeeleygib/databricks-sql-mcp:latest
```

### Configuring Claude Desktop

Add the server to your Claude Desktop config file:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "databricks-sql": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e", "DATABRICKS_HOST=https://your-workspace.azuredatabricks.net",
        "-e", "DATABRICKS_TOKEN=dapi1234567890abcdef",
        "-e", "DATABRICKS_WAREHOUSE_ID=abc123def456",
        "bkeeleygib/databricks-sql-mcp:latest"
      ]
    }
  }
}
```

**Important:** Replace the placeholder values with your actual credentials, then restart Claude Desktop.

### Configuring Claude Code (CLI)

Use the Claude Code CLI to register the server directly:

```bash
claude mcp add-json databricks-sql '{
  "command": "docker",
  "args": [
    "run", "-i", "--rm",
    "-e", "DATABRICKS_HOST=https://your-workspace.azuredatabricks.net",
    "-e", "DATABRICKS_TOKEN=dapi1234567890abcdef",
    "-e", "DATABRICKS_WAREHOUSE_ID=abc123def456",
    "bkeeleygib/databricks-sql-mcp:latest"
  ]
}'
```

## Example Queries

Once connected, you can ask Claude:

**Browsing:**
- "List all catalogs in my Unity Catalog"
- "Show me the schemas in the `analytics` catalog"
- "What tables are in `analytics.silver`?"
- "Describe the schema of `analytics.silver.customers`"

**Querying:**
- "Run: `SELECT * FROM analytics.silver.customers LIMIT 10`"
- "Show me the top 5 most expensive items"
- "What's the total revenue by category?"

## Security Notes

**Never commit your `.env` file or credentials to Git!**

- The `.env` file is listed in `.gitignore`
- Each user needs their own Databricks personal access token
- The Docker image does **not** contain any credentials
- Credentials are passed at runtime via environment variables

## Development

### Local Development (without Docker)

Requires **Python 3.11+**.

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file with your credentials
cp .env.example .env
# Edit .env with your values

# Run the server
python server.py
```

### Project Structure

```
server.py          # MCP server implementation (FastMCP + Databricks SDK)
requirements.txt   # Python dependencies (pinned to major versions)
Dockerfile         # Docker image definition
install.sh         # Quick installer for Mac/Linux
install.bat        # Quick installer for Windows
.env.example       # Template for environment variables
```

## Troubleshooting

**"Error: DATABRICKS_WAREHOUSE_ID not set"**
- Make sure you passed all three environment variables
- Check that your `.env` file has values for `DATABRICKS_HOST`, `DATABRICKS_TOKEN`, and `DATABRICKS_WAREHOUSE_ID`

**"Query failed: ..."**
- Verify your credentials are correct
- Check that the SQL Warehouse is running (it may be auto-suspended)
- Ensure you have permissions to access the requested data

**"Server disconnected"**
- Restart Claude Desktop or start a new Claude Code session
- Verify Docker is running: `docker info`
- Check that the container starts successfully: `docker run -i --rm --env-file .env bkeeleygib/databricks-sql-mcp:latest`

**"Tables show as false"**
- This bug has been fixed in the latest version
- Pull the latest image: `docker pull bkeeleygib/databricks-sql-mcp:latest`

## License

[MIT](LICENSE)
