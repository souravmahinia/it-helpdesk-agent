import sqlite3
import os

# This tells Python where to create the database file
DB_PATH = os.path.join(os.path.dirname(__file__), "helpdesk.db")

def get_connection():
    # Creates and returns a connection to our database
    return sqlite3.connect(DB_PATH)

def setup_database():
    conn = get_connection()
    cursor = conn.cursor()

    # Create tickets table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            ticket_id TEXT PRIMARY KEY,
            user_email TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT DEFAULT 'open',
            created_at TEXT,
            processed_at TEXT,
            action_taken TEXT,
            ai_classification TEXT
        )
    """)

    # Create action logs table
    # This stores every action the AI agent takes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS action_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id TEXT NOT NULL,
            action_type TEXT NOT NULL,
            action_details TEXT,
            status TEXT DEFAULT 'success',
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Database created successfully!")

def insert_tickets_from_csv(df):
    conn = get_connection()
    cursor = conn.cursor()

    inserted = 0
    skipped = 0

    for _, row in df.iterrows():
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO tickets 
                (ticket_id, user_email, description, status, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                row['ticket_id'],
                row['user_email'],
                row['description'],
                row['status'],
                row['created_at']
            ))
            if cursor.rowcount > 0:
                inserted += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"Error inserting ticket {row['ticket_id']}: {e}")

    conn.commit()
    conn.close()
    print(f"✅ Inserted {inserted} tickets | Skipped {skipped} duplicates")


def get_all_tickets():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tickets ORDER BY created_at DESC")
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    conn.close()
    return [dict(zip(columns, row)) for row in rows]

def update_ticket_status(ticket_id, status, action_taken, ai_classification):
    """Updates a ticket after the AI agent processes it."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE tickets 
        SET status = ?, 
            action_taken = ?, 
            ai_classification = ?,
            processed_at = CURRENT_TIMESTAMP
        WHERE ticket_id = ?
    """, (status, action_taken, ai_classification, ticket_id))

    conn.commit()
    conn.close()


def log_action(ticket_id, action_type, action_details, status="success"):
    """Logs every action the agent takes — critical for real systems."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO action_logs (ticket_id, action_type, action_details, status)
        VALUES (?, ?, ?, ?)
    """, (ticket_id, action_type, action_details, status))

    conn.commit()
    conn.close()

def get_action_logs():
    """Fetches all action logs — shows what the agent did."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM action_logs ORDER BY timestamp DESC")
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    conn.close()
    return [dict(zip(columns, row)) for row in rows]

if __name__ == "__main__":
    import pandas as pd
    setup_database()
    df = pd.read_csv("data/sample_tickets.csv")
    insert_tickets_from_csv(df)
    
    print("\n--- Tickets in Database ---")
    tickets = get_all_tickets()
    for ticket in tickets:
        print(ticket)
