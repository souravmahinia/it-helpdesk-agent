import pandas as pd

def read_tickets(file_path):
    
    # Read the CSV file into a DataFrame
    df = pd.read_csv(file_path)
    
    # Filter only open tickets
    open_tickets = df[df['status'] == 'open']
    
    print(f"Total tickets found: {len(df)}")
    print(f"Open tickets to process: {len(open_tickets)}")
    print("\n--- Ticket List ---")
    
    # Loop through each ticket and print details
    for index, ticket in open_tickets.iterrows():
        print(f"\nTicket ID  : {ticket['ticket_id']}")
        print(f"User       : {ticket['user_email']}")
        print(f"Description: {ticket['description']}")
        print(f"Status     : {ticket['status']}")

if __name__ == "__main__":
    read_tickets("data/sample_tickets.csv")
