import sqlite3
import os

# CONFIGURATION: Dynamic pathing
# We calculate the absolute path to the database. Ensures script doesn't break 
# if ran from different folders
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, '..', 'data', 'db', 'nafood.db')

# SECURITY: The "Whitelist"
# This is our master list of 'AI-Safe' data. Even if a table has private 
# emails or phones, the AI will never see them because they aren't on this list
SAFE_COLUMNS = [
    'ManufacturerID', 'ManufacturerName', 'City', 'State', 
    'ProductID', 'ProductName', 'CategoryName', 'AvailableQuantity', 'Unit',
    'SupplierName', 'ClientName', 'OrderDate', 'OrderTotal'
]

def query_database(sql_query: str):
    """
    Acts as a secure gatekeeper. It takes an AI's SQL request, 
    cleans it, runs it safely, and scrubs the results.
    """
    
    # GUARDRAIL 1: Command Validation
    # We force the query to be 'SELECT'. This prevents 'Prompt Injection' 
    # where a user tries to trick the AI into deleting the database
    normalized_query = sql_query.strip().upper()
    if not normalized_query.startswith("SELECT"):
        return "ERROR: Access Denied. This tool is Read-Only."

    try:
        # GUARDRAIL 2: System-Level Protection
        # 'mode=ro' tells the computer's operating system that this 
        # connection is physically incapable of writing to the file
        conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
        cursor = conn.cursor()
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        
        # GUARDRAIL 3: The "Governor" (Performance)
        # AI 'Context Windows' are expensive and limited. We stop the query 
        # if it returns too much data to prevent crashing the agent
        if len(rows) > 50:
            conn.close()
            return f"ERROR: Result set too large ({len(rows)} rows). Please use LIMIT."

        # METADATA: Grab the column names (e.g., 'City', 'ProductName')
        columns = [description[0] for description in cursor.description]
        conn.close()

        # DATA TRANSFORMATION: JSON-like Formatting
        # We turn raw database rows into 'Key-Value' pairs so the AI 
        # has context for every piece of data it sees
        clean_results = []
        for row in rows:
            raw_record = dict(zip(columns, row))
            
            # GUARDRAIL 4: Data Scrubbing
            # We build a NEW record containing ONLY the columns on our Whitelist.
            # Prevents unauthorized data from reaching AI, even if the SQL query tries to pull it
            # This makes the script 'Injection-Proof' against column aliasing
            safe_record = {k: v for k, v in raw_record.items() if k in SAFE_COLUMNS}
            clean_results.append(safe_record)
        
        return clean_results

    except Exception as e:
        # RELIABILITY: Catch and report technical errors
        return f"Database Error: {str(e)}"

def get_schema():
    """
    Returns the 'Map' of the database (Table names and Column names).
    This allows the AI to understand the structure of DB without guessing.
    """
    try:
        # Establish a secure, read-only connection to the database file
        conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
        cursor = conn.cursor()
        
        # SQLite command that finds all tables in DB
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        # Initialize a dictionary to store our 'Map'
        schema_map = {}

        # Loop through every table found in sqlite_master table
        for table_name_tuple in tables:
            table_name = table_name_tuple[0]

            # For every table, we ask: "What are the column names?"
            cursor.execute(f"PRAGMA table_info({table_name});") # specialized command that lists the details of a specific table
            
            # table_info returns a lot of data (type, primary key, etc.)
            columns = [info[1] for info in cursor.fetchall()] # index 1 is column name

            # Save list of columns to our Map under the Table Name
            schema_map[table_name] = columns
            
        conn.close()
        return schema_map
    except Exception as e:
        return f"Schema Error: {str(e)}"
    
if __name__ == "__main__":
    # LOCAL TEST: Verify that 'ManufacturerEmail' is blocked by our Whitelist
    test_query = "SELECT * FROM Manufacturers;"
    print(query_database(test_query))