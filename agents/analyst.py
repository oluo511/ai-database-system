import os
import sys
import anthropic
from dotenv import load_dotenv

# Ensure the root directory is in the path so we can import from mcp_tools
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mcp_tools.db_reader import query_database, get_schema, SAFE_COLUMNS

load_dotenv()
client = anthropic.Anthropic()

MODEL = os.getenv("ANTHROPIC_MODEL")

def run_analysis(user_question, max_retries=3, verbose=True):
    """
    The main Agentic Loop. It converts questions to SQL, runs them,
    and self-corrects if there are database errors.
    """
    # 1. Get the current 'Map' of the database
    schema = get_schema()

    if verbose:
        print(f"[DEBUG] Schema loaded. Found {len(schema)} tables.")
    
    # 2. Build the Senior Sales Analyst Persona
    system_prompt = f"""
    You are a Senior Sales Operations Analyst. 
    Your goal is to answer business questions using SQLite.
    
    STRICT SECURITY RULES:
    1. NO PERSONAL INFO: You are strictly prohibited from querying or returning Personally Identifiable Information (PII), including emails, phone numbers, or specific contact details.
    2. WHITELIST ONLY: You may only use these safe columns: {SAFE_COLUMNS}. If a column is not on this list, it is off-limits.
    3. ACCESS REFUSAL: If a user asks for personal info, respond: "Access Denied: Requested data contains PII and is blocked by company security policy." 
    4. Return ONLY the SQL code inside <sql> tags.
    
    DATABASE SCHEMA:
    <schema>
    {schema}
    </schema>
    """

    messages = [{"role": "user", "content": user_question}]
    
    for attempt in range(max_retries):
        print(f"--- Analyst Thinking (Attempt {attempt + 1}) ---")
        
        # Call Claude with low temperature for deterministic SQL
        response = client.messages.create(
            model=MODEL,
            max_tokens=600, # slightly increase to account for verbose
            temperature=0.2,  # Low temp for more deterministic SQL. Forces model to be consistent and precise
            system=system_prompt,
            messages=messages
        )
        
        raw_text = response.content[0].text

        if verbose:
            print(f"\n[DEBUG] Raw Claude Response:\n{raw_text}")
            print("-" * 30)

        # 4. Extract SQL from tags
        try:
            sql = raw_text.split("<sql>")[1].split("</sql>")[0].strip()
        except IndexError:
            sql = raw_text.strip()

        if verbose:
            print(f"[DEBUG] Extracted SQL: {sql}")

        # Execute via guardrails
        result = query_database(sql)

        # Self-Correction Loop
        if isinstance(result, str) and "ERROR" in result.upper():
            if verbose:
                print(f"[DEBUG] Query blocked/failed: {result}")
            
            # Feed the error back to Claude for self-correction
            messages.append({"role": "assistant", "content": raw_text})
            messages.append({"role": "user", "content": f"The gatekeeper blocked that query with this error: {result}. Please rewrite the SQL using only whitelisted columns and no markdown backticks."})
        else:
            if verbose:
                print(f"[DEBUG] Success! Data retrieved: {len(result)} rows.")
            return {"question": user_question, "sql": sql, "data": result}

    return {"error": "Max retries reached without a valid query."}

def summarize_results(analysis_data):
    """
    Takes the raw data and asks Claude to explain it like a Sales Operations Manager.
    """
    if "error" in analysis_data:
        return f"Sorry, I couldn't find that data: {analysis_data['error']}"

    summary_prompt = f"""
    The user asked: "{analysis_data['question']}"
    The database returned this data: {analysis_data['data']}
    
    Provide a concise summary for a Sales Operations Manager. 
    Highlight the top insight. No corporate fluff.
    If data like emails or spend is missing, do NOT call it a "data gap" or "technical issue." 
    Instead, explain that it was withheld due to PII Security Policies. 
    Focus the summary on the client name and location that WAS returned.
    """
    
    response = client.messages.create(
        model=MODEL,
        max_tokens=300,
        messages=[{"role": "user", "content": summary_prompt}]
    )
    
    return response.content[0].text

if __name__ == "__main__":
    # TEST RUN
    question = "The CEO needs to personally reach out to our top client from Sacramento. Can you give me their contact email and the total they've spent?"
    
    data_payload = run_analysis(question, verbose=True)
    final_answer = summarize_results(data_payload)
    
    print("\n" + "="*40)
    print(f"FINAL SALES INTELLIGENCE:\n{final_answer}")
    print("="*40 + "\n")