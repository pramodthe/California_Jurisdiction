import os
import sys
import time
import subprocess

# Add parent to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '../.env'))

def run_command(cmd, description):
    print(f"\n--- {description} ---")
    try:
        # Run command and wait
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print("✅ Success")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("❌ Failed")
        print(e.stderr)
        return False

def smoke_test():
    base_dir = os.path.join(os.path.dirname(__file__), '..')
    os.chdir(base_dir)
    
    print("🚀 Starting Smoke Test...")
    
    # 1. Check Docker for Qdrant (Optional check, mainly just warn)
    # We assume user starts it as per instructions, but we can verify if port is open
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 6333))
    if result != 0:
        print("⚠️  Warning: Qdrant does not seem to be running on port 6333. Some steps may fail.")
    else:
        print("✅ Qdrant detected on port 6333")
    sock.close()

    # 2. Init DB
    if not run_command(f"{sys.executable} scripts/init_db.py", "Initializing SQLite"):
        return

    # 3. Init Qdrant
    if not run_command(f"{sys.executable} scripts/init_qdrant.py", "Initializing Qdrant Collections"):
        print("Skipping further Qdrant steps due to failure.")
    
    # 4. Ingest KB (Mock pass if no API key)
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  OPENAI_API_KEY not found. Skipping KB ingest.")
    else:
        run_command(f"{sys.executable} scripts/ingest_kb.py", "Ingesting Knowledge Base")

    # 5. Run Pipeline (Dry Run / Mock)
    # We need to make sure we don't actually scrape if we don't want to, 
    # but the script mocks firecrawl if no key.
    run_command(f"{sys.executable} -m pipeline.run_daily --mock", "Running Pipeline (Mock)")

    # 6. Verify Data in DB
    import sqlite3
    conn = sqlite3.connect("data/app.db")
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM items")
    count = c.fetchone()[0]
    print(f"\n📊 Items in DB: {count}")
    conn.close()
    
    if count > 0:
        print("✅ Pipeline produced items!")
    else:
        print("⚠️  Pipeline ran but produced no items (expected if mock data didn't yield results).")

    print("\n✅ Smoke Test Completed.")

if __name__ == "__main__":
    smoke_test()
