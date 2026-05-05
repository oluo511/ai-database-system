import os
import sys
import anthropic
from dotenv import load_dotenv

# adds the root directory to the Python path so it can find mcp_tools instead of running it from agents
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mcp_tools.db_reader import SAFE_COLUMNS

load_dotenv()
client = anthropic.Anthropic()

MODEL = os.getenv("ANTHROPIC_MODEL")

def run_qa_check(user_question, analyst_sql, database_results, verbose=True):
    """
    Acts as a final gatekeeper. Reviews Analyst output for 
    logical errors or security breaches.
    """
    
    qa_prompt = f"""
    You are a Senior QA Data Engineer. You are reviewing an AI Analyst's work.
    
    USER QUESTION: {user_question}
    ANALYST SQL: {analyst_sql}
    RESULT DATA: {database_results}
    
    AUDIT CHECKLIST:
    1. Does the SQL logic actually answer the user's intent?
    2. Are there any PII leaks (emails/phones) not in {SAFE_COLUMNS}?
    3. Is the math for unit conversions (e.g., lbs to kg) logically sound?
    
    If it passes, return "PASS". 
    If it fails, explain exactly why so the Analyst can fix it.
    """

    if verbose:
        print(f"[DEBUG] QA Input Question: {user_question}")
        print(f"[DEBUG] QA Checking SQL: {analyst_sql}")

    # Calling Claude with temperature 0 for maximum precision
    response = client.messages.create(
        model=MODEL,
        max_tokens=500,
        temperature=0,
        messages=[{"role": "user", "content": qa_prompt}]
    )

    result = response.content[0].text

    if verbose:
        print(f"\n[DEBUG] QA Review Results:\n{result}")
        print("-" * 30)

    return result

if __name__ == "__main__":
    # TEST RUN
    test_q = "We want to restock the Smoked Salmon. Find the top 3 cheapest Smoked Salmon per kg"
    test_sql = "SELECT SupplierName, list_price_per_kg FROM mart_product_pricing WHERE ProductName = 'Smoked Salmon' ORDER BY list_price_per_kg ASC LIMIT 1;"
    test_data = [{"SupplierName": "Fresh Horizon Foods", "list_price_per_kg": 19.0}]
    
    print("--- Running QA Audit ---")
    audit_result = run_qa_check(test_q, test_sql, test_data)
    print(f"Audit Result: {audit_result}")