import sqlite3
import os
import sys

# Add parent directory to path to import config if needed
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

DB_PATH = os.path.join(os.path.dirname(__file__), '../data/app.db')
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), '../pipeline/db/schema.sql')

def init_db():
    print(f"Initializing database at {DB_PATH}...")
    
    # Ensure data directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    with open(SCHEMA_PATH, 'r') as f:
        schema = f.read()
        cursor.executescript(schema)
        
    conn.commit()
    conn.close()
    print("Database initialized successfully.")

if __name__ == "__main__":
    init_db()
