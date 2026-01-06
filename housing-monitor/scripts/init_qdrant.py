import os
import sys
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

# Add parent directory to path to import collections config
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from pipeline.vector.collections import KB_COLLECTION_NAME, LEGISLATION_COLLECTION_NAME, VECTOR_SIZE, DISTANCE_METRIC

from pipeline.config import QDRANT_URL

def init_qdrant():
    print(f"Connecting to Qdrant at {QDRANT_URL}...")
    client = QdrantClient(url=QDRANT_URL)
    
    # Create KB collection
    if not client.collection_exists(KB_COLLECTION_NAME):
        print(f"Creating collection: {KB_COLLECTION_NAME}")
        client.create_collection(
            collection_name=KB_COLLECTION_NAME,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=DISTANCE_METRIC),
        )
    else:
        print(f"Collection {KB_COLLECTION_NAME} already exists.")

    # Create Legislation collection
    if not client.collection_exists(LEGISLATION_COLLECTION_NAME):
        print(f"Creating collection: {LEGISLATION_COLLECTION_NAME}")
        client.create_collection(
            collection_name=LEGISLATION_COLLECTION_NAME,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=DISTANCE_METRIC),
        )
    else:
        print(f"Collection {LEGISLATION_COLLECTION_NAME} already exists.")
        
    print("Qdrant initialized successfully.")

if __name__ == "__main__":
    init_qdrant()
