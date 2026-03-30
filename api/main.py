import os
import sys
from fastapi import FastAPI, HTTPException
from typing import Optional

# Add parent folder to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_setup import get_all_tickets, get_action_logs

# Initialize FastAPI app
app = FastAPI(
    title="IT Helpdesk AI Agent API",
    description="AI-powered IT helpdesk automation system",
    version="1.0.0"
)


@app.get("/")
async def root():
    """Health check — tells you the API is running."""
    return {
        "message": "IT Helpdesk AI Agent API is running",
        "status": "healthy"
    }


@app.get("/tickets")
async def get_tickets(status: Optional[str] = None):
    """
    Returns all tickets from database.
    Optional filter: /tickets?status=open
    """
    tickets = get_all_tickets()

    if status:
        tickets = [t for t in tickets if t['status'] == status]

    return {
        "total": len(tickets),
        "tickets": tickets
    }


@app.get("/tickets/{ticket_id}")
async def get_ticket(ticket_id: str):
    """Returns a single ticket by ID."""
    tickets = get_all_tickets()
    ticket = next((t for t in tickets if t['ticket_id'] == ticket_id), None)

    if not ticket:
        raise HTTPException(status_code=404, detail=f"Ticket {ticket_id} not found")

    return ticket


@app.get("/logs")
async def get_logs():
    """Returns all action logs — what the AI agent did."""
    logs = get_action_logs
    return {
        "total": len(logs),
        "logs": logs
    }


@app.get("/stats")
async def get_stats():
    """Returns summary statistics for the dashboard."""
    tickets = get_all_tickets()

    total = len(tickets)
    resolved = len([t for t in tickets if t['status'] == 'resolved'])
    escalated = len([t for t in tickets if t['status'] == 'escalated'])
    open_tickets = len([t for t in tickets if t['status'] == 'open'])

    return {
        "total_tickets": total,
        "resolved": resolved,
        "escalated": escalated,
        "open": open_tickets,
        "resolution_rate": f"{(resolved/total*100):.1f}%" if total > 0 else "0%"
    }


@app.post("/run-pipeline")
async def run_pipeline():
    """Triggers the full AI agent pipeline."""
    try:
        from agent.helpdesk_agent import run_pipeline as execute_pipeline
        csv_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "data", "sample_tickets.csv"
        )
        execute_pipeline(csv_path)
        return {"status": "success", "message": "Pipeline completed!"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# uvicorn api.main:app --reload


# INFO: Uvicorn running on http://127.0.0.1:8000


# Now open your browser and go to:

# http://127.0.0.1:8000/docs