from mcp.server.fastmcp import FastMCP
from agents.orchestrator import run_orchestrated_query
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize the MCP server
mcp = FastMCP("BusinessIntelligence")

@mcp.tool()
def ask_bi_agent(question: str) -> str:
    """
    The primary interface for the BI Lead. This tool uses reasoning to
    consult business rules, visualize schemas, and run SQL queries
    to provide executive-level insights.
    """
    return run_orchestrated_query(question)

if __name__ == "__main__":
    # stdio transport is required for Kiro/Claude Desktop MCP integration
    mcp.run(transport="stdio")
