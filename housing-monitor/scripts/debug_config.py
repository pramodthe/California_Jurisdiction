import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from pipeline.config import QDRANT_URL, SQLITE_PATH

print(f"DEBUG: QDRANT_URL in config: {QDRANT_URL}")
print(f"DEBUG: SQLITE_PATH in config: {SQLITE_PATH}")
