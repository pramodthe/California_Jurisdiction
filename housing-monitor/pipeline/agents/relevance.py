import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pipeline.rag.retrieve import RAGRetriever
from pipeline.config import RELEVANCE_THRESHOLD

class RelevanceAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0)
        self.retriever = RAGRetriever()
        
    def classify(self, doc: dict) -> dict:
        """
        Classifies a document for relevance using RAG.
        Returns the updated doc dict with relevance fields.
        """
        # Construct query from title + start of content
        query = f"{doc.get('title', '')} {doc.get('content_text', '')[:500]}"
        
        # 1. Retrieve Context
        kb_context = self.retriever.retrieve(query)
        
        # 2. Prompt LLM
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You classify whether a document is relevant to California housing legislation (rent control, tenant protections, fair housing, eviction/just cause, landlord obligations, fees/deposits, enforcement, registration, housing policy affecting landlords/tenants). You must follow the relevance policy and use retrieved KB context.

GLOSSARY / EXAMPLES (KB):
{kb_chunks}

Return STRICT JSON ONLY with this schema:
{{
  "is_relevant": boolean,
  "relevance_score": number,  // 0.0 to 1.0
  "topics": ["rent_control"|"fair_housing"|"eviction"|"fees_deposits"|"registration"|"enforcement"|"zoning_supply"|"voucher_soi"|"other"],
  "rationale": string,        // <= 40 words
  "confidence": number        // 0.0 to 1.0
}}

Rules:
- If the doc is about general housing programs with no regulatory/legislative change, set is_relevant=false unless it changes landlord/tenant obligations.
- If unclear, set is_relevant=false with a low score and explain uncertainty."""),
            ("user", """DOCUMENT METADATA:
county: {county}
source_type: {source_type}
title: {title}
url: {url}

DOCUMENT TEXT (partial):
{document_text}""")
        ])
        
        chain = prompt | self.llm
        
        try:
            response = chain.invoke({
                "kb_chunks": kb_context,
                "county": doc.get('county'),
                "source_type": doc.get('source_type'),
                "title": doc.get('title'),
                "url": doc.get('url'),
                "document_text": doc.get('content_text', '')[:3000] # Limit context window
            })
            
            content = response.content.strip()
            # Clean up potential markdown formatting in JSON
            if content.startswith("```json"):
                content = content[7:-3]
            
            result = json.loads(content)
            
            # Enforce strict boolean based on threshold if LLM is fuzzy, but LLM usually handles 'is_relevant'.
            # We can override if score is low but is_relevant is true, or vice versa if needed.
            # config.RELEVANCE_THRESHOLD can be used to filter downstream.
            
            doc['is_relevant'] = result.get('is_relevant', False)
            doc['relevance_score'] = result.get('relevance_score', 0.0)
            doc['topics'] = result.get('topics', [])
            doc['relevance_rationale'] = result.get('rationale', '')
            doc['ai_confidence'] = result.get('confidence', 0.0)
            
            return doc
            
        except Exception as e:
            print(f"Relevance agent error: {e}")
            doc['is_relevant'] = False
            doc['relevance_score'] = 0.0
            doc['error'] = str(e)
            return doc

if __name__ == "__main__":
    # Test
    agent = RelevanceAgent()
    doc = {
        "title": "Rent Control Ordinance Update",
        "content_text": "The city council discusses amending the rent stabilization ordinance to cap increases at 3%.",
        "county": "Los Angeles",
        "source_type": "agenda",
        "url": "http://example.com"
    }
    print(agent.classify(doc))
