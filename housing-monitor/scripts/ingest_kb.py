import os
import sys
import glob
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Qdrant
from qdrant_client import QdrantClient
from dotenv import load_dotenv

# Load env vars
load_dotenv(os.path.join(os.path.dirname(__file__), '../.env'))

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from pipeline.vector.collections import KB_COLLECTION_NAME

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
KB_DIR = os.path.join(os.path.dirname(__file__), '../kb')

def ingest_kb():
    print(f"Loading KB from {KB_DIR}...")
    
    client = QdrantClient(url=QDRANT_URL)
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not found in environment.")
        return

    documents = []
    for file_path in glob.glob(os.path.join(KB_DIR, "*.md")):
        print(f"Loading {os.path.basename(file_path)}...")
        loader = TextLoader(file_path)
        docs = loader.load()
        # Add metadata source
        for doc in docs:
            doc.metadata["source"] = os.path.basename(file_path)
        documents.extend(docs)

    if not documents:
        print("No documents found.")
        return

    print(f"Splitting {len(documents)} documents...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Generated {len(chunks)} chunks.")

    print(f"Ingesting into Qdrant collection '{KB_COLLECTION_NAME}'...")
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    # Initialize VectorStore with existing collection
    qdrant_store = Qdrant(
        client=client,
        collection_name=KB_COLLECTION_NAME,
        embeddings=embeddings
    )
    
    # Add documents
    qdrant_store.add_documents(chunks)
    
    print("KB ingestion complete.")

if __name__ == "__main__":
    ingest_kb()
