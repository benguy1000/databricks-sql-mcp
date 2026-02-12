from dotenv import load_dotenv
load_dotenv()

from fastmcp import FastMCP
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.sql import StatementState
import os

# Create MCP server
mcp = FastMCP("databricks-sql")

# Initialize Databricks client (will use environment variables)
def get_client():
    """Get authenticated Databricks client"""
    return WorkspaceClient(
        host=os.getenv("DATABRICKS_HOST"),
        token=os.getenv("DATABRICKS_TOKEN")
    )

@mcp.tool()
def execute_sql(query: str, warehouse_id: str = None) -> str:
    """
    Execute a SQL query on Databricks.

    When working with wesley_farms catalog tables, consider using get_table_relationships
    first to understand proper join logic.

    Args:
        query: SQL query to execute
        warehouse_id: Optional SQL warehouse ID (uses default if not provided)

    Returns:
        Query results as formatted text
    """
    try:
        client = get_client()
        
        # Use provided warehouse_id or get from environment
        if not warehouse_id:
            warehouse_id = os.getenv("DATABRICKS_WAREHOUSE_ID")
        
        if not warehouse_id:
            return "Error: No warehouse_id provided and DATABRICKS_WAREHOUSE_ID not set"
        
        # Execute the query
        result = client.statement_execution.execute_statement(
            statement=query,
            warehouse_id=warehouse_id
        )
        
        # Wait for completion
        if result.status.state == StatementState.FAILED:
            return f"Query failed: {result.status.error.message}"
        
        # Format results
        if not result.result:
            return "Query executed successfully (no results returned)"
        
        # Get column names
        columns = [col.name for col in result.manifest.schema.columns]
        
        # Get data rows
        rows = []
        if result.result.data_array:
            for row in result.result.data_array:
                rows.append(row)
        
        # Format as table
        output = f"Columns: {', '.join(columns)}\n\n"
        output += f"Rows returned: {len(rows)}\n\n"
        
        # Show first 10 rows
        for i, row in enumerate(rows[:10]):
            output += f"Row {i+1}: {dict(zip(columns, row))}\n"
        
        if len(rows) > 10:
            output += f"\n... and {len(rows) - 10} more rows"
        
        return output
        
    except Exception as e:
        return f"Error executing query: {str(e)}"


@mcp.tool()
def get_table_relationships() -> str:
    """
    Get predefined table join relationships from wesley_farms.gold.table_relationships.
    Use this when querying tables in the wesley_farms catalog to understand how tables
    should be joined together.

    Returns:
        Formatted table join relationships showing how to join tables
    """
    try:
        client = get_client()
        warehouse_id = os.getenv("DATABRICKS_WAREHOUSE_ID")

        if not warehouse_id:
            return "Error: DATABRICKS_WAREHOUSE_ID not set"

        # Query the table relationships metadata
        result = client.statement_execution.execute_statement(
            statement="SELECT * FROM wesley_farms.gold.table_relationships",
            warehouse_id=warehouse_id
        )

        # Check for query failure
        if result.status.state == StatementState.FAILED:
            return f"Query failed: {result.status.error.message}"

        # Format results
        if not result.result or not result.result.data_array:
            return "No table relationships found in wesley_farms.gold.table_relationships"

        # Get column names
        columns = [col.name for col in result.manifest.schema.columns]

        # Get data rows
        rows = result.result.data_array

        # Format as readable join relationships
        output = "TABLE JOIN RELATIONSHIPS (wesley_farms.gold)\n"
        output += "=" * 60 + "\n\n"
        output += f"Total relationships defined: {len(rows)}\n\n"

        for i, row in enumerate(rows, 1):
            row_dict = dict(zip(columns, row))
            output += f"Relationship {i}:\n"
            for col, val in row_dict.items():
                output += f"  {col}: {val}\n"
            output += "\n"

        return output

    except Exception as e:
        return f"Error retrieving table relationships: {str(e)}"


@mcp.tool()
def list_databases() -> str:
    """List all databases/schemas in the Databricks workspace"""
    try:
        client = get_client()
        warehouse_id = os.getenv("DATABRICKS_WAREHOUSE_ID")
        
        if not warehouse_id:
            return "Error: DATABRICKS_WAREHOUSE_ID not set"
        
        result = client.statement_execution.execute_statement(
            statement="SHOW DATABASES",
            warehouse_id=warehouse_id
        )
        
        # Extract database names
        databases = []
        if result.result and result.result.data_array:
            databases = [row[0] for row in result.result.data_array]
        
        return f"Databases found: {len(databases)}\n\n" + "\n".join(f"- {db}" for db in databases)
        
    except Exception as e:
        return f"Error listing databases: {str(e)}"


@mcp.tool()
def list_tables(database: str) -> str:
    """
    List all tables in a specific database.
    
    Args:
        database: Name of the database to list tables from
    """
    try:
        client = get_client()
        warehouse_id = os.getenv("DATABRICKS_WAREHOUSE_ID")
        
        if not warehouse_id:
            return "Error: DATABRICKS_WAREHOUSE_ID not set"
        
        result = client.statement_execution.execute_statement(
            statement=f"SHOW TABLES IN {database}",
            warehouse_id=warehouse_id
        )
        
        # Extract table names
        tables = []
        if result.result and result.result.data_array:
            # Get column names to understand structure
            columns = [col.name for col in result.manifest.schema.columns]
            
            # Find the tableName column index
            table_name_idx = None
            for i, col in enumerate(columns):
                if col.lower() in ['tablename', 'table']:
                    table_name_idx = i
                    break
            
            if table_name_idx is None:
                # Fallback: assume it's column 1
                table_name_idx = 1
            
            # Extract table names using the correct column
            for row in result.result.data_array:
                if len(row) > table_name_idx and row[table_name_idx]:
                    tables.append(str(row[table_name_idx]))
        
        if not tables:
            return f"No tables found in '{database}' or unable to parse results"
        
        return f"Tables in '{database}': {len(tables)}\n\n" + "\n".join(f"- {table}" for table in tables)
        
    except Exception as e:
        return f"Error listing tables: {str(e)}"


@mcp.tool()
def describe_table(database: str, table: str) -> str:
    """
    Get schema information for a specific table.
    
    Args:
        database: Name of the database
        table: Name of the table
    """
    try:
        client = get_client()
        warehouse_id = os.getenv("DATABRICKS_WAREHOUSE_ID")
        
        if not warehouse_id:
            return "Error: DATABRICKS_WAREHOUSE_ID not set"
        
        result = client.statement_execution.execute_statement(
            statement=f"DESCRIBE {database}.{table}",
            warehouse_id=warehouse_id
        )
        
        # Format schema information
        output = f"Schema for {database}.{table}:\n\n"
        
        if result.result and result.result.data_array:
            for row in result.result.data_array:
                col_name = row[0]
                col_type = row[1]
                col_comment = row[2] if len(row) > 2 else ""
                output += f"  {col_name}: {col_type}"
                if col_comment:
                    output += f" -- {col_comment}"
                output += "\n"
        
        return output
        
    except Exception as e:
        return f"Error describing table: {str(e)}"

@mcp.tool()
def list_catalogs() -> str:
    """List all catalogs in the Unity Catalog metastore"""
    try:
        client = get_client()
        warehouse_id = os.getenv("DATABRICKS_WAREHOUSE_ID")
        
        if not warehouse_id:
            return "Error: DATABRICKS_WAREHOUSE_ID not set"
        
        result = client.statement_execution.execute_statement(
            statement="SHOW CATALOGS",
            warehouse_id=warehouse_id
        )
        
        # Extract catalog names
        catalogs = []
        if result.result and result.result.data_array:
            catalogs = [row[0] for row in result.result.data_array]
        
        return f"Catalogs found: {len(catalogs)}\n\n" + "\n".join(f"- {cat}" for cat in catalogs)
        
    except Exception as e:
        return f"Error listing catalogs: {str(e)}"


@mcp.tool()
def list_schemas(catalog: str) -> str:
    """
    List all schemas/databases in a specific catalog.
    
    Args:
        catalog: Name of the catalog
    """
    try:
        client = get_client()
        warehouse_id = os.getenv("DATABRICKS_WAREHOUSE_ID")
        
        if not warehouse_id:
            return "Error: DATABRICKS_WAREHOUSE_ID not set"
        
        result = client.statement_execution.execute_statement(
            statement=f"SHOW SCHEMAS IN {catalog}",
            warehouse_id=warehouse_id
        )
        
        # Extract schema names
        schemas = []
        if result.result and result.result.data_array:
            schemas = [row[0] for row in result.result.data_array]
        
        return f"Schemas in '{catalog}': {len(schemas)}\n\n" + "\n".join(f"- {schema}" for schema in schemas)
        
    except Exception as e:
        return f"Error listing schemas: {str(e)}"


@mcp.tool()
def list_tables_full(catalog: str, schema: str) -> str:
    """
    List all tables in a specific catalog and schema.
    
    Args:
        catalog: Name of the catalog
        schema: Name of the schema/database
    """
    try:
        client = get_client()
        warehouse_id = os.getenv("DATABRICKS_WAREHOUSE_ID")
        
        if not warehouse_id:
            return "Error: DATABRICKS_WAREHOUSE_ID not set"
        
        result = client.statement_execution.execute_statement(
            statement=f"SHOW TABLES IN {catalog}.{schema}",
            warehouse_id=warehouse_id
        )
        
        # Extract table names
        tables = []
        if result.result and result.result.data_array:
            # Get column names to understand structure
            columns = [col.name for col in result.manifest.schema.columns]
            
            # Find the tableName column index
            table_name_idx = None
            for i, col in enumerate(columns):
                if col.lower() in ['tablename', 'table']:
                    table_name_idx = i
                    break
            
            if table_name_idx is None:
                # Fallback: assume it's column 1 (typical for SHOW TABLES)
                table_name_idx = 1
            
            # Extract table names using the correct column
            for row in result.result.data_array:
                if len(row) > table_name_idx and row[table_name_idx]:
                    tables.append(str(row[table_name_idx]))
        
        if not tables:
            return f"No tables found in '{catalog}.{schema}' or unable to parse results"
        
        return f"Tables in '{catalog}.{schema}': {len(tables)}\n\n" + "\n".join(f"- {table}" for table in tables)
        
    except Exception as e:
        return f"Error listing tables: {str(e)}"


@mcp.tool()
def describe_table_full(catalog: str, schema: str, table: str) -> str:
    """
    Get schema information for a specific table using full 3-part name.
    
    Args:
        catalog: Name of the catalog
        schema: Name of the schema/database
        table: Name of the table
    """
    try:
        client = get_client()
        warehouse_id = os.getenv("DATABRICKS_WAREHOUSE_ID")
        
        if not warehouse_id:
            return "Error: DATABRICKS_WAREHOUSE_ID not set"
        
        result = client.statement_execution.execute_statement(
            statement=f"DESCRIBE {catalog}.{schema}.{table}",
            warehouse_id=warehouse_id
        )
        
        # Format schema information
        output = f"Schema for {catalog}.{schema}.{table}:\n\n"
        
        if result.result and result.result.data_array:
            for row in result.result.data_array:
                col_name = row[0]
                col_type = row[1]
                col_comment = row[2] if len(row) > 2 else ""
                output += f"  {col_name}: {col_type}"
                if col_comment:
                    output += f" -- {col_comment}"
                output += "\n"
        
        return output
        
    except Exception as e:
        return f"Error describing table: {str(e)}"

if __name__ == "__main__":
    mcp.run()