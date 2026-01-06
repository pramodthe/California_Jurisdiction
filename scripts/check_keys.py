import os
import requests
from dotenv import load_dotenv

# Load env from ../housing-monitor/.env
env_path = os.path.join(os.path.dirname(__file__), '../housing-monitor/.env')
print(f"Loading env from {env_path}")
load_dotenv(env_path)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")

def check_openai():
    print("\n--- Testing OpenAI ---")
    if not OPENAI_API_KEY:
        print("❌ OPENAI_API_KEY not found in env")
        return
        
    try:
        headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
        resp = requests.get("https://api.openai.com/v1/models", headers=headers, timeout=10)
        if resp.status_code == 200:
            print("✅ OpenAI API Key is VALID (Models list retrieved)")
        else:
            print(f"❌ OpenAI API Key INVALID. Status: {resp.status_code}")
            print(resp.text[:200])
    except Exception as e:
        print(f"❌ OpenAI Check Failed: {e}")

def check_firecrawl():
    print("\n--- Testing Firecrawl ---")
    if not FIRECRAWL_API_KEY:
        print("❌ FIRECRAWL_API_KEY not found in env")
        return
        
    try:
        # Check credit usage or basic scrape (scrape is safer/standard)
        # Using /v1/scrape with a dummy URL
        url = "https://api.firecrawl.dev/v1/scrape"
        headers = {
            "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {"url": "https://example.com"}
        
        resp = requests.post(url, json=data, headers=headers, timeout=10)
        if resp.status_code == 200:
            print("✅ Firecrawl API Key is VALID")
        else:
            print(f"❌ Firecrawl API Key INVALID/Error. Status: {resp.status_code}")
            print(resp.text[:200])
    except Exception as e:
        print(f"❌ Firecrawl Check Failed: {e}")

if __name__ == "__main__":
    check_openai()
    check_firecrawl()
