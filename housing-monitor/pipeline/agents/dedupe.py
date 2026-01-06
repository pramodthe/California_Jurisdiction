import sqlite3
from langchain_openai import OpenAIEmbeddings
from qdrant_client import QdrantClient
from pipeline.config import QDRANT_URL, DEDUPE_SIM_THRESHOLD, SQLITE_PATH
from pipeline.vector.collections import LEGISLATION_COLLECTION_NAME

class DedupeAgent:
    def __init__(self):
        self.client = QdrantClient(url=QDRANT_URL)
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        print(f"DEBUG: DedupeAgent connecting to SQLite at: {SQLITE_PATH}")
        self.conn = sqlite3.connect(SQLITE_PATH) 
        # Note: In a real app, use a connection pool or persistent connection managed properly
        self.conn.row_factory = sqlite3.Row

    def get_existing_by_url(self, url_normalized: str):
        c = self.conn.cursor()
        c.execute('''
            SELECT i.id, i.title, i.summary 
            FROM items i 
            JOIN raw_documents r ON i.raw_document_id = r.id
            WHERE r.url_normalized = ?
        ''', (url_normalized,))
        return c.fetchone()

    def get_existing_by_hash(self, content_hash: str):
        c = self.conn.cursor()
        c.execute('''
            SELECT i.id, i.title, i.summary 
            FROM items i 
            JOIN raw_documents r ON i.raw_document_id = r.id
            WHERE r.content_hash = ?
        ''', (content_hash,))
        return c.fetchone()

    def check_semantic_duplicate(self, text: str, county: str):
        # Embed current text
        vector = self.embeddings.embed_query(text)
        
        # Search in Qdrant, filtering by county if we stored payload properly
        # For simplicity, we search global or add filter logic
        hits = self.client.query_points(
            collection_name=LEGISLATION_COLLECTION_NAME,
            query=vector,
            limit=1,
            score_threshold=DEDUPE_SIM_THRESHOLD
        ).points
        
        if hits:
            return hits[0]
        return None

    def process(self, doc: dict) -> dict:
        """
        Checks for duplicates.
        Returns doc with is_new, dedup_reason, matched_item_id.
        """
        doc['is_new'] = True
        doc['dedup_reason'] = None
        doc['matched_item_id'] = None

        # 1. URL Check
        existing_url = self.get_existing_by_url(doc.get('url_normalized', ''))
        if existing_url:
            doc['is_new'] = False
            doc['dedup_reason'] = 'url'
            doc['matched_item_id'] = existing_url['id']
            return doc

        # 2. Hash Check
        existing_hash = self.get_existing_by_hash(doc.get('content_hash', ''))
        if existing_hash:
            doc['is_new'] = False
            doc['dedup_reason'] = 'hash'
            doc['matched_item_id'] = existing_hash['id']
            return doc
            
        # 3. Semantic Check (Only if text is substantial)
        content = doc.get('content_text', '')
        if len(content) > 100:
            hit = self.check_semantic_duplicate(content[:2000], doc.get('county'))
            if hit:
                doc['is_new'] = False
                doc['dedup_reason'] = f'semantic (score {hit.score:.2f})'
                # Assuming payload has item_id
                doc['matched_item_id'] = hit.payload.get('item_id')
                return doc

        return doc
        
    def close(self):
        self.conn.close()

if __name__ == "__main__":
    d = DedupeAgent()
    # Test would require DB state
    d.close()
