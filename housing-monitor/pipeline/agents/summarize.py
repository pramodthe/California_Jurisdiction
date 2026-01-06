import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

class SummarizeAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0)
        
    def summarize(self, doc: dict) -> dict:
        """
        Generates a structured summary for the document.
        Adds summary fields to the doc dict.
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You write concise, plain-English structured summaries of county housing legislation or policy actions. Do not invent facts. If dates are missing, say "unknown" and lower confidence.

Return STRICT JSON ONLY with this schema:
{{
  "heading": string,
  "summary": string,              // 3-6 sentences
  "key_points": string[],         // 3-7 bullets
  "impacted_parties": string[],   // e.g., ["tenants","landlords","property_managers"]
  "important_dates": string[],    // e.g., ["2026-02-10 public hearing"] or []
  "source_link": string,
  "date_posted": string,          // ISO date or "unknown"
  "ai_confidence": number         // 0.0 to 1.0
}}

Rules:
- Use only information supported by the text.
- If the doc is an agenda/minutes, summarize the specific housing-related agenda items."""),
            ("user", """DOCUMENT METADATA:
county: {county}
title: {title}
url: {url}
extracted_date: {extracted_date}

DOCUMENT TEXT:
{document_text}""")
        ])
        
        chain = prompt | self.llm
        
        try:
            response = chain.invoke({
                "county": doc.get('county'),
                "title": doc.get('title'),
                "url": doc.get('url'),
                "extracted_date": doc.get('extracted_date'),
                "document_text": doc.get('content_text', '')[:5000] # Limit context
            })
            
            content = response.content.strip()
            if content.startswith("```json"):
                content = content[7:-3]
                
            result = json.loads(content)
            
            doc.update(result)
            return doc
            
        except Exception as e:
            print(f"Summarize agent error: {e}")
            doc['error_summary'] = str(e)
            return doc

if __name__ == "__main__":
    s = SummarizeAgent()
    doc = {
        "title": "Test Doc",
        "content_text": "The board approved a new rent production program starting Jan 1, 2026.",
        "county": "Test County",
        "url": "http://test.com",
        "extracted_date": "2026-01-01"
    }
    print(s.summarize(doc))
