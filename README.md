# 🤖 IT Helpdesk AI Agent

> **From RPA to Agentic AI** — Rebuilding IT automation with intelligence.

---

## 💡 The Story Behind This Project

For 4 years, I built Python-based RPA automation for IT operations — specifically automating ServiceNow ticket workflows for password resets and user access management.

Those systems worked. But they were brittle.

A ticket that said *"I can't get into my account"* would fail because it didn't contain the keyword *"password."* Every edge case needed a new rule. Every new rule needed maintenance.

**This project is the upgrade.**

Instead of rigid IF/ELSE rules, this system uses a Large Language Model (LLM) to *understand* what the user needs — regardless of how they write it. The same ticket that broke my old RPA bot? This agent handles it instantly.

---

## 🎯 What This Project Does

An end-to-end AI-powered IT helpdesk automation system that:

- **Reads** IT support tickets from any source (CSV, API, database)
- **Understands** ticket intent using LangChain + OpenAI — no keyword matching
- **Classifies** each ticket automatically into the right action type
- **Executes** the appropriate action (password reset, access grant, access revoke)
- **Logs** every action to a database for full audit trail
- **Displays** everything on a live Streamlit dashboard
- **Exposes** the entire pipeline as a REST API via FastAPI

---

## 🏗️ Architecture

```
IT Tickets (CSV / ServiceNow API)
           ↓
   ETL Pipeline (Python + Pandas)
   Extract → Transform → Load
           ↓
   SQLite Database (raw ticket storage)
           ↓
   AI Agent (LangChain + OpenAI GPT)
   Reads ticket → Understands intent → Decides action
           ↓
   Action Execution
   PASSWORD_RESET / ACCESS_GRANT / ACCESS_REVOKE / ESCALATE
           ↓
   Audit Log (SQLite)
           ↓
   FastAPI REST API + Streamlit Dashboard
```

---

## ⚙️ Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Language | Python 3.11 | Core language for all logic |
| AI Framework | LangChain | Connects LLM to pipeline |
| LLM | OpenAI GPT-3.5 | Understands natural language tickets |
| Data Processing | Pandas | ETL — extract and transform tickets |
| Database | SQLite | Store tickets and action logs |
| API Layer | FastAPI | Expose agent as production REST API |
| Dashboard | Streamlit | Visual interface for monitoring |
| Cloud Ready | AWS S3, Glue, Lambda | Production deployment path |

---

## 📁 Project Structure

```
it-helpdesk-agent/
├── data/
│   └── sample_tickets.csv        # Sample IT tickets dataset
├── database/
│   └── db_setup.py               # SQLite schema + all CRUD operations
├── agent/
│   └── helpdesk_agent.py         # Core AI agent + ETL pipeline
├── api/
│   └── main.py                   # FastAPI REST API with 5 endpoints
├── app/
│   └── streamlit_app.py          # Live monitoring dashboard
├── requirements.txt
├── .env.example
└── .gitignore
```

---

## 🚀 How to Run

### Step 1 — Clone the repo
```bash
git clone https://github.com/souravmahinia/it-helpdesk-agent.git
cd it-helpdesk-agent
```

### Step 2 — Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

### Step 3 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4 — Add your OpenAI API key
```bash
cp .env.example .env
# Open .env and add your OpenAI API key
```

### Step 5 — Setup database
```bash
python database/db_setup.py
```

### Step 6 — Run the AI Agent pipeline
```bash
python agent/helpdesk_agent.py
```

### Step 7 — Launch the dashboard
```bash
streamlit run app/streamlit_app.py
```

### Optional — Run the REST API
```bash
uvicorn api.main:app --reload
# Visit http://localhost:8000/docs
```

---

## 🧠 How the AI Agent Works

The agent classifies each ticket into one of four action types:

| Classification | Trigger | Action |
|---|---|---|
| `PASSWORD_RESET` | User cannot login, forgot password, account locked | Reset password, send link |
| `ACCESS_GRANT` | User needs access to a system or resource | Submit access request, trigger approval |
| `ACCESS_REVOKE` | Access needs to be removed | Revoke access, terminate sessions |
| `UNKNOWN` | Cannot determine intent | Escalate to human agent |

**The key difference from RPA:**
Old RPA systems matched keywords. If a user wrote *"I am unable to get into my account"* — no keyword match, ticket unresolved.

This agent reads the sentence like a human and still correctly classifies it as `PASSWORD_RESET`. That's the power of LLM-based automation.

---

## 📊 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Health check |
| GET | `/tickets` | Get all tickets |
| GET | `/tickets?status=open` | Filter tickets by status |
| GET | `/tickets/{ticket_id}` | Get single ticket |
| GET | `/stats` | Summary statistics |
| GET | `/logs` | All agent action logs |
| POST | `/run-pipeline` | Trigger full AI pipeline |

Visit `http://localhost:8000/docs` for interactive API documentation.

---

## 🔮 Production Roadmap

In a real production environment this system would be extended with:

- **RAG (Retrieval Augmented Generation)** — Agent reads internal IT policy documents before classifying, giving policy-aware responses
- **ServiceNow / Jira API** — Replace CSV with live ticket ingestion
- **Active Directory / Okta API** — Replace simulated actions with real access management calls
- **AWS Lambda + EventBridge** — Serverless deployment with scheduled triggers
- **AWS RDS (PostgreSQL)** — Replace SQLite with production database
- **Slack notifications** — Alert team when tickets are escalated
- **Monitoring + Alerting** — Track agent accuracy and pipeline health

---

## 🔗 Related Projects

- [AWS ETL Pipeline](https://github.com/souravmahinia) — S3 + Glue + Athena data pipeline

---

## 👨‍💻 About

4 years of Python automation experience in IT operations, now building AI-powered systems that bring intelligence to the automation work I've always done.

**Skills:** Python • LangChain • OpenAI API • FastAPI • Streamlit • SQL • ETL • AWS • RPA Automation

---

## 📄 License

MIT License — feel free to use and modify.
