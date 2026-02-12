@echo off
REM ============================================================
REM Databricks SQL MCP Server - Installer for Windows
REM ============================================================

echo.
echo ==============================================
echo   Databricks SQL MCP Server - Quick Install
echo ==============================================
echo.
echo This script will configure Claude Desktop to
echo use the Databricks SQL MCP server via Docker.
echo.

REM Check prerequisites
where docker >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo ERROR: Docker is not installed or not in PATH.
    echo Please install Docker first: https://docs.docker.com/get-docker/
    exit /b 1
)

where claude >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo ERROR: Claude CLI is not installed or not in PATH.
    echo Please install Claude CLI first: https://docs.anthropic.com/en/docs/claude-code
    exit /b 1
)

echo -- Prerequisites OK (Docker + Claude CLI found)
echo.

REM Prompt for credentials
echo Enter your Databricks credentials.
echo (See README for help finding these values)
echo.

set /p DATABRICKS_HOST="Databricks Host URL (e.g. https://adb-123.azuredatabricks.net): "
if "%DATABRICKS_HOST%"=="" (
    echo ERROR: Databricks Host URL is required.
    exit /b 1
)

set /p DATABRICKS_TOKEN="Databricks Personal Access Token (starts with dapi...): "
if "%DATABRICKS_TOKEN%"=="" (
    echo ERROR: Databricks Token is required.
    exit /b 1
)

set /p DATABRICKS_WAREHOUSE_ID="SQL Warehouse ID: "
if "%DATABRICKS_WAREHOUSE_ID%"=="" (
    echo ERROR: SQL Warehouse ID is required.
    exit /b 1
)

echo.
echo -- Pulling Docker image...
docker pull bkeeleygib/databricks-sql-mcp:latest

echo.
echo -- Configuring Claude Desktop...

claude mcp add-json databricks-sql "{\"command\":\"docker\",\"args\":[\"run\",\"-i\",\"--rm\",\"-e\",\"DATABRICKS_HOST=%DATABRICKS_HOST%\",\"-e\",\"DATABRICKS_TOKEN=%DATABRICKS_TOKEN%\",\"-e\",\"DATABRICKS_WAREHOUSE_ID=%DATABRICKS_WAREHOUSE_ID%\",\"bkeeleygib/databricks-sql-mcp:latest\"]}"

echo.
echo ==============================================
echo   Installation Complete!
echo ==============================================
echo.
echo The 'databricks-sql' MCP server has been added
echo to your Claude Desktop configuration.
echo.
echo Next steps:
echo   1. Restart Claude Desktop completely
echo   2. Ask Claude: "List all catalogs in my Unity Catalog"
echo.
echo To verify your config:
echo   type "%APPDATA%\Claude\claude_desktop_config.json"
echo.
