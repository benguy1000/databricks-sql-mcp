# Databricks SQL MCP Server

A Model Context Protocol (MCP) server for executing SQL queries on Databricks with full Unity Catalog support.

## Features

**Basic Tools:**
- `execute_sql` - Run any SQL query
- `list_databases` - Show databases (default catalog)
- `list_tables` - Show tables in a database
- `describe_table` - Show table schema

**Unity Catalog Tools:**
- `list_catalogs` - Show all Unity Catalog catalogs
- `list_schemas` - Show schemas in a specific catalog
- `list_tables_full` - Show tables with full 3-part naming (catalog.schema.table)
- `describe_table_full` - Describe table with full catalog path

## Unity Catalog Hierarchy
```
CATALOG (e.g., wesley_farms)
  └── SCHEMA/DATABASE (e.g., silver)
      └── TABLE (e.g., customers)
```

**Full qualified name:** `catalog.schema.table` (e.g., `wesley_farms.silver.customers`)

## Prerequisites

- Docker installed
- Databricks workspace access
- Databricks personal access token
- SQL Warehouse ID

## Getting Your Databricks Credentials

### 1. Databricks Host URL
Your workspace URL, e.g., `https://adb-1234567890.azuredatabricks.net`

### 2. Personal Access Token
1. Open Databricks workspace
2. Click your username (top-right)
3. Go to "User Settings" → "Developer" → "Access tokens"
4. Click "Generate new token"
5. Copy the token (starts with `dapi...`)

### 3. SQL Warehouse ID
1. Go to "SQL Warehouses" in Databricks
2. Click on a warehouse
3. Copy the warehouse ID from the URL (between `/warehouses/` and `?`)

## Running with Docker

### Build the Image
```bash
docker build -t databricks-sql-mcp .
```

### Run with Environment Variables
```bash
docker run -i --rm \
  -e DATABRICKS_HOST="https://your-workspace.azuredatabricks.net" \
  -e DATABRICKS_TOKEN="dapi1234567890abcdef" \
  -e DATABRICKS_WAREHOUSE_ID="abc123def456" \
  databricks-sql-mcp
```

### Run with .env File

Create a `.env` file with your credentials:
```
DATABRICKS_HOST=https://your-workspace.azuredatabricks.net
DATABRICKS_TOKEN=dapi1234567890abcdef
DATABRICKS_WAREHOUSE_ID=abc123def456
```

Then run:
```bash
docker run -i --rm --env-file .env databricks-sql-mcp
```

## Using with Claude Desktop

### Configuration File Location

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`  
**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

### Add to Configuration
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
        "databricks-sql-mcp"
      ]
    }
  }
}
```

**Important:** Replace with your actual credentials!

Then restart Claude Desktop completely.

## Example Queries

Once connected to Claude Desktop, you can ask Claude:

**Browsing:**
- "List all catalogs in my Unity Catalog"
- "Show me schemas in the wesley_farms catalog"
- "What tables are in wesley_farms.silver?"
- "Describe the schema of wesley_farms.silver.customers"

**Querying:**
- "Run this SQL: SELECT * FROM wesley_farms.silver.customers LIMIT 10"
- "Show me the top 5 most expensive items"
- "What's the total revenue by category?"

## Security Notes

⚠️ **Never commit your .env file or credentials to Git!**

- The `.env` file is in `.gitignore`
- Each user needs their own Databricks credentials
- Personal access tokens should be kept secret
- The Docker image does NOT contain credentials

## Development

### Local Development (without Docker)
```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file with your credentials
# (see .env.example)

# Run the server
python server.py
```

### Install in Claude Desktop (Dev Mode)
```bash
fastmcp install claude-desktop server.py --name databricks-sql --env-file .env
```

Then restart Claude Desktop.

## Troubleshooting

**"Error: DATABRICKS_WAREHOUSE_ID not set"**
- Make sure you passed all environment variables
- Check that your .env file has all three values

**"Query failed: ..."**
- Verify your credentials are correct
- Check that the SQL Warehouse is running
- Ensure you have permissions to access the data

**"Server disconnected"**
- Restart Claude Desktop
- Check Docker is running
- Verify the container started successfully

**Tables show as "false"**
- This bug has been fixed in the latest version
- Rebuild your Docker image: `docker build -t databricks-sql-mcp .`

## License

MIT