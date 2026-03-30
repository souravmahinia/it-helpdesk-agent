import streamlit as st
import pandas as pd
import sys
import os

# Add parent folder to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_setup import get_all_tickets, get_action_logs

# ─────────────────────────────────────────────
# PAGE SETUP
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="IT Helpdesk AI Agent",
    page_icon="🤖",
    layout="wide"
)

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────

st.title("🤖 IT Helpdesk AI Agent Dashboard")
st.markdown("""
AI-powered system that automatically reads IT support tickets, 
classifies them using LLMs, and resolves them automatically.
""")
st.divider()

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────

with st.sidebar:
    st.header("⚙️ Controls")

    if st.button("🚀 Run Agent Pipeline", use_container_width=True, type="primary"):
        with st.spinner("AI Agent is processing tickets..."):
            try:
                from agent.helpdesk_agent import run_pipeline
                csv_path = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "data", "sample_tickets.csv"
                )
                run_pipeline(csv_path)
                st.success("✅ Pipeline completed!")
            except Exception as e:
                st.error(f"Error: {str(e)}")

    st.divider()
    status_filter = st.selectbox(
        "Filter by Status",
        ["All", "open", "resolved", "escalated"]
    )

# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────

try:
    tickets = get_all_tickets()
    logs = get_action_logs()
except Exception as e:
    st.error(f"Database not found. Run the pipeline first. Error: {e}")
    tickets = []
    logs = []

# ─────────────────────────────────────────────
# METRICS
# ─────────────────────────────────────────────

st.subheader("📊 Summary")

col1, col2, col3, col4 = st.columns(4)

total = len(tickets)
resolved = len([t for t in tickets if t['status'] == 'resolved'])
escalated = len([t for t in tickets if t['status'] == 'escalated'])
open_tickets = len([t for t in tickets if t['status'] == 'open'])

with col1:
    st.metric("Total Tickets", total)
with col2:
    st.metric("✅ Resolved", resolved)
with col3:
    st.metric("❓ Escalated", escalated)
with col4:
    st.metric("🔵 Open", open_tickets)

st.divider()

# ─────────────────────────────────────────────
# TICKETS TABLE
# ─────────────────────────────────────────────

st.subheader("🎫 Ticket Queue")

if tickets:
    df = pd.DataFrame(tickets)

    if status_filter != "All":
        df = df[df['status'] == status_filter]

    st.dataframe(df[[
        'ticket_id', 'user_email', 'description',
        'ai_classification', 'status', 'action_taken'
    ]], use_container_width=True)
else:
    st.info("No tickets found. Click 'Run Agent Pipeline' to process tickets.")

st.divider()

# ─────────────────────────────────────────────
# ACTION LOGS
# ─────────────────────────────────────────────

st.subheader("📋 Agent Action Logs")
st.markdown("Every action the AI agent takes is logged here.")

if logs:
    logs_df = pd.DataFrame(logs)
    st.dataframe(logs_df, use_container_width=True)
else:
    st.info("No logs yet. Run the pipeline to see agent activity.")

st.divider()

# ─────────────────────────────────────────────
# HOW IT WORKS
# ─────────────────────────────────────────────

with st.expander("🔍 How This System Works"):
    st.markdown("""
    **Pipeline Flow:**
    
    1. **Extract** — Tickets loaded from CSV
    2. **Load** — Raw tickets stored in SQLite database
    3. **AI Classification** — LangChain + OpenAI reads each ticket and classifies it
    4. **Action Execution** — Agent performs the appropriate action
    5. **Logging** — Every action logged to database for audit trail
    6. **Dashboard** — This Streamlit UI shows real time status
    
    **In Production:**
    - CSV replaced by ServiceNow or Jira API
    - Simulated actions replaced by real Active Directory or AWS IAM calls
    - Deployed on AWS EC2 with scheduled triggers
    """)

st.caption("Built with Python | LangChain | OpenAI | SQLite | FastAPI | Streamlit")

# Now open a **new terminal** (keep FastAPI running in the old one) and run:
# streamlit run app/streamlit_app.py