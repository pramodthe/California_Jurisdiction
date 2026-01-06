import qdrant_client
from qdrant_client import QdrantClient
import sys

# DEBUG: Check module path
print(f"QdrantClient module: {qdrant_client.__file__}")

try:
    # Use port 6343 as discovered
    url = "http://localhost:6343"
    print(f"Connecting to {url}...")
    client = QdrantClient(url=url)
    
    # 1. Check Collections (Connectivity proof)
    cols = client.get_collections()
    print(f"SUCCESS. Connected. Collections found: {len(cols.collections)}")
    for c in cols.collections:
        print(f" - {c.name}")
        if c.name == "legislation_chunks":
             count = client.count(c.name)
             print(f"   (Points: {count.count})")

except Exception as e:
    print(f"FAILED to connect: {e}")
