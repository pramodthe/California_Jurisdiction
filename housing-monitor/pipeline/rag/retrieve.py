from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Qdrant
from qdrant_client import QdrantClient
from pipeline.config import QDRANT_URL
from pipeline.vector.collections import KB_COLLECTION_NAME

class RAGRetriever:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self.client = QdrantClient(url=QDRANT_URL)
        self.vector_store = Qdrant(
            client=self.client,
            collection_name=KB_COLLECTION_NAME,
            embeddings=self.embeddings
        )


    def retrieve(self, query: str, top_k: int = 3) -> str:
        """
        Retrieve relevant chunks from the Knowledge Base.
        Returns a formatted string of context.
        """
        try:
            # Embed the query
            query_vector = self.embeddings.embed_query(query)
            
            # Search Qdrant
            # qdrant-client v1.10+ uses query_points or search (but search is missing here)
            # Using query_points which is robust
            search_result = self.client.query_points(
                collection_name=KB_COLLECTION_NAME,
                query=query_vector,
                limit=top_k,
                with_payload=True
            )
            
            docs = search_result.points
            
            context_parts = []
            for i, point in enumerate(docs):
                payload = point.payload or {}
                content = payload.get('page_content', '')
                source = payload.get('metadata', {}).get('source', 'unknown')
                context_parts.append(f"--- CHUNK {i+1} (Source: {source}) ---\n{content}")
            
            return "\n\n".join(context_parts)
        except Exception as e:
            print(f"RAG retrieval error: {e}")
            return ""
            
if __name__ == "__main__":
    r = RAGRetriever()
    print(r.retrieve("rent control caps"))
