from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Any
import logging
from pipeline.config import RELEVANCE_THRESHOLD
from pipeline.agents.relevance import RelevanceAgent
from pipeline.agents.dedupe import DedupeAgent
from pipeline.agents.summarize import SummarizeAgent
import pipeline.db.crud as crud
from langchain_openai import OpenAIEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct
from pipeline.config import QDRANT_URL
from pipeline.vector.collections import LEGISLATION_COLLECTION_NAME

logger = logging.getLogger(__name__)

# Define the State of the graph
class PipelineState(TypedDict):
    raw_document_id: int
    doc: dict
    status: str

# Initialize Agents
relevance_agent = RelevanceAgent()
dedupe_agent = DedupeAgent()
summarize_agent = SummarizeAgent()
client = QdrantClient(url=QDRANT_URL)
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

def load_doc(state: PipelineState):
    # In a real batch flow, we might load from DB here if we only passed ID.
    # For now, we assume 'doc' is populated by the runner or pre-loader.
    # If not, fetch by raw_document_id.
    return state

def classify_relevance(state: PipelineState):
    logger.info(f"Classifying doc {state['raw_document_id']}")
    updated_doc = relevance_agent.classify(state['doc'])
    return {"doc": updated_doc}

def check_dedupe(state: PipelineState):
    logger.info(f"Checking duplicates for doc {state['raw_document_id']}")
    updated_doc = dedupe_agent.process(state['doc'])
    return {"doc": updated_doc}

def summarize(state: PipelineState):
    logger.info(f"Summarizing doc {state['raw_document_id']}")
    updated_doc = summarize_agent.summarize(state['doc'])
    return {"doc": updated_doc}

def persist(state: PipelineState):
    logger.info(f"Persisting doc {state['raw_document_id']}")
    doc = state['doc']
    
    # Ensure raw_document_id is linked for the Join
    doc['raw_document_id'] = state['raw_document_id']
    
    # 1. Save to SQLite
    item_id = crud.insert_processed_item(doc)
    
    # 2. Save to Qdrant if relevant and new and has content
    if doc.get('is_relevant') and doc.get('is_new') and doc.get('content_text'):
        try:
            vector = embeddings.embed_query(doc['content_text'][:8000])
            payload = {
                "item_id": item_id,
                "title": doc.get('title'),
                "county": doc.get('county'),
                "url": doc.get('url')
            }
            client.upsert(
                collection_name=LEGISLATION_COLLECTION_NAME,
                points=[
                    PointStruct(
                        id=item_id, # Use item_id as integer ID
                        vector=vector,
                        payload=payload
                    )
                ]
            )
        except Exception as e:
            logger.error(f"Failed to upsert to Qdrant: {e}")
            
    return {"status": "completed"}

# Define conditions
def relevance_condition(state: PipelineState):
    if state['doc'].get('is_relevant') and state['doc'].get('relevance_score', 0) >= RELEVANCE_THRESHOLD:
        return "relevant"
    return "not_relevant"

def dedupe_condition(state: PipelineState):
    if state['doc'].get('is_new'):
        return "new"
    return "duplicate"

# Build Graph
workflow = StateGraph(PipelineState)

workflow.add_node("classify", classify_relevance)
workflow.add_node("dedupe", check_dedupe)
workflow.add_node("summarize", summarize)
workflow.add_node("persist", persist)

workflow.set_entry_point("classify")

workflow.add_conditional_edges(
    "classify",
    relevance_condition,
    {
        "relevant": "dedupe",
        "not_relevant": "persist" # We still persist non-relevant items to track they were processed
    }
)

workflow.add_conditional_edges(
    "dedupe",
    dedupe_condition,
    {
        "new": "summarize",
        "duplicate": "persist" # We persist duplicates to track the match
    }
)

workflow.add_edge("summarize", "persist")
workflow.add_edge("persist", END)

app_graph = workflow.compile()
