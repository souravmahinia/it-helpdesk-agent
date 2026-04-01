import os
import sys
from dotenv import load_dotenv
from rag_pipeline import get_relevant_policy
# Load your API key from .env file
load_dotenv()

# Add parent folder to path so we can import database module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

def classify_ticket(ticket_description, user_email):
    """
    This function sends a ticket to OpenAI and gets back
    a classification of what action is needed.
    
    This replaces your old RPA rules like:
    IF description contains "password" → reset
    
    Now the AI understands ANY description naturally.
    """

    # Initialize the LLM
    # Temperature 0 means consistent answers — good for classification
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0,
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )

    # This is your prompt — instructions you give to the AI
    # Think of it as writing a job description for the AI
    # RAG — Get relevant policy for this ticket
    # This is the key upgrade from basic agent to RAG-powered agent
    print(f"   🔍 Searching IT policy for relevant rules...")
    relevant_policy = get_relevant_policy(ticket_description)

    prompt = ChatPromptTemplate.from_template("""
    You are an intelligent IT helpdesk agent working for TechCorp India.
    Before taking any action, you must follow the company IT policy strictly.
    
    COMPANY IT POLICY (retrieved specifically for this ticket):
    {policy_context}
    
    Based on the above policy, classify this ticket and respond accordingly.
    
    Classify the ticket into EXACTLY one of these categories:
    - PASSWORD_RESET: user needs password reset or account unlock
    - ACCESS_GRANT: user needs access to a system or resource  
    - ACCESS_REVOKE: access needs to be removed for a user
    - UNKNOWN: cannot determine the action needed
    
    Also identify:
    - The target system mentioned (AWS, VPN, HR Portal, Finance, SAP etc). Say 'general' if not mentioned.
    - Priority: HIGH if it blocks work completely, MEDIUM if it slows work, LOW otherwise
    - Policy note: any specific policy rule that applies to this ticket
    
    Respond in this EXACT format:
    ACTION: <action_type>
    SYSTEM: <target_system>
    PRIORITY: <priority>
    POLICY_NOTE: <specific policy rule that applies>
    REASON: <one line explanation>
    
    User Email: {user_email}
    Ticket: {description}
    """)

    chain = prompt | llm

    response = chain.invoke({
        "user_email": user_email,
        "description": ticket_description,
        "policy_context": relevant_policy
    })
    # print(response)

    return response.content


def parse_classification(response_text):
    """
    The AI returns text like:
    ACTION: PASSWORD_RESET
    SYSTEM: VPN
    PRIORITY: HIGH
    REASON: User cannot login due to expired password
    
    This function converts that text into a Python dictionary
    so we can use each value separately in our code.
    """
    result = {
        "action_type": "UNKNOWN",
        "target_system": "general",
        "priority": "MEDIUM",
        "policy_note": "",
        "reason": ""
    }

    for line in response_text.strip().split('\n'):
        if line.startswith("ACTION:"):
            result["action_type"] = line.replace("ACTION:", "").strip()
        elif line.startswith("SYSTEM:"):
            result["target_system"] = line.replace("SYSTEM:", "").strip()
        elif line.startswith("PRIORITY:"):
            result["priority"] = line.replace("PRIORITY:", "").strip()
        elif line.startswith("REASON:"):
            result["reason"] = line.replace("REASON:", "").strip()
        elif line.startswith("POLICY_NOTE:"):
            result["policy_note"] = line.replace("POLICY_NOTE:", "").strip()

    return result

def execute_action(ticket_id, user_email, action_type, target_system, policy_note=""):
    """
    Executes the action based on AI classification.
    In production these would be real API calls to 
    Active Directory, AWS IAM, or Okta.
    For now we simulate and log the actions.
    """
    
    if action_type == "PASSWORD_RESET":
        result = f"Password reset initiated for {user_email} on {target_system}. Policy: {policy_note}"
        print(f"   🔑 PASSWORD RESET: {user_email} | System: {target_system}")
        print(f"   📋 Policy Applied: {policy_note}")

    elif action_type == "ACCESS_GRANT":
        result = f"Access request for {target_system} submitted for {user_email}. Manager approval triggered.Policy: {policy_note}"
        print(f"   ✅ ACCESS GRANT: {user_email} | System: {target_system}")
        print(f"   📋 Policy Applied: {policy_note}")

    elif action_type == "ACCESS_REVOKE":
        result = f"Access revoked for {user_email} on {target_system}. All sessions terminated.Policy: {policy_note}"
        print(f"   🚫 ACCESS REVOKE: {user_email} | System: {target_system}")
        print(f"   📋 Policy Applied: {policy_note}")

    else:
        result = f"Ticket escalated to human agent — could not classify request."
        print(f"   ❓ ESCALATED: {ticket_id}")

    return result


def run_pipeline(csv_path):
    """
    Main pipeline — connects everything together.
    Extract → Load → Classify → Act → Log
    """
    import pandas as pd
    from database.db_setup import (
        setup_database,
        insert_tickets_from_csv,
        update_ticket_status,
        log_action,
        get_all_tickets
    )

    print("\n" + "="*50)
    print("🤖 IT HELPDESK AI AGENT STARTING")
    print("="*50)

    # Setup database
    setup_database()

    # Extract tickets from CSV
    print("\n📂 Reading tickets from CSV...")
    df = pd.read_csv(csv_path)
    open_tickets = df[df['status'] == 'open']
    print(f"✅ Found {len(open_tickets)} open tickets")

    # Load into database
    insert_tickets_from_csv(open_tickets)

    # Process each ticket with AI
    print("\n📋 Processing tickets with AI...\n")
    processed = 0
    errors = 0

    for _, ticket in open_tickets.iterrows():
        print(f"🎫 {ticket['ticket_id']} | {ticket['user_email']}")

        try:
            # Step 1 — Classify with AI
            response = classify_ticket(ticket['description'], ticket['user_email'])
            parsed = parse_classification(response)
            print(f"   📌 {parsed['action_type']} | Priority: {parsed['priority']}")

            # Step 2 — Execute action
            action_result = execute_action(
                ticket_id=ticket['ticket_id'],
                user_email=ticket['user_email'],
                action_type=parsed['action_type'],
                target_system=parsed['target_system'],
                policy_note=parsed['policy_note']
            )

            # Step 3 — Update ticket in database
            update_ticket_status(
                ticket_id=ticket['ticket_id'],
                status="resolved" if parsed['action_type'] != "UNKNOWN" else "escalated",
                action_taken=action_result,
                ai_classification=parsed['action_type']
            )

            # Step 4 — Log the action
            log_action(
                ticket_id=ticket['ticket_id'],
                action_type=parsed['action_type'],
                action_details=action_result,
                status="success"
            )

            processed += 1

        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            errors += 1

    # Summary
    print("\n" + "="*50)
    print(f"✅ Pipeline Complete!")
    print(f"   Processed: {processed} tickets")
    print(f"   Errors: {errors} tickets")
    print("="*50)

# Test the classifier with one ticket
if __name__ == "__main__":
    csv_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data", "sample_tickets.csv"
    )
    run_pipeline(csv_path)


# Raw AI Response:
# ACTION: PASSWORD_RESET
# SYSTEM: general
# PRIORITY: HIGH
# REASON: User cannot login due to forgotten password

# Parsed Result:
# {'action_type': 'PASSWORD_RESET', 'target_system': 'general', 'priority': 'HIGH', 'reason': 'User cannot login due to forgotten password'}