from mcp.server.fastmcp import FastMCP
from agents.analyst import run_analysis
from agents.qa import run_qa_check

# Initialize the server
mcp = FastMCP("BusinessIntelligence")

@mcp.tool()
def analyze_sales_data(question: str):
    """Answers sales questions by generating and running SQL."""
    return run_analysis(question)

@mcp.tool()
def audit_query(question: str, sql: str, data: list):
    """Reviews SQL and data for logical errors or PII leaks."""
    return run_qa_check(question, sql, data)

if __name__ == "__main__":
    mcp.run()