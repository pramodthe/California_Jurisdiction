import time
from typing import List, Dict, Any
from pipeline.config import SOURCES
from pipeline.collector.firecrawl_client import FirecrawlClient
from pipeline.collector.normalize import normalize_url, compute_content_hash
import pipeline.db.crud as crud
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class Collector:
    def __init__(self, mock: bool = False):
        self.firecrawl = FirecrawlClient(mock=mock)
        self.sources = SOURCES

    def run(self) -> List[int]:
        """
        Runs the collection process for all sources.
        Returns a list of raw_document_ids that were newly added.
        """
        new_doc_ids = []
        for source in self.sources:
            url = source['url']
            county = source['county']
            source_type = source['source_type']
            
            logger.info(f"Collecting from {county} ({source_type}): {url}")
            
            # Simple scrape of the seed URL
            # In a real app, this might crawl subpages or RSS feeds
            result = self.firecrawl.scrape_url(url)
            
            if result:
                 # result might be a dict (mock) or a Pydantic model (Firecrawl)
                 if isinstance(result, dict):
                     content = result.get('markdown') or result.get('content', '')
                     metadata = result.get('metadata', {})
                 else:
                     # Basic normalize (Handle Pydantic object)
                     content = getattr(result, 'markdown', None) or getattr(result, 'content', '')
                     # Metadata might be an object or dict? Pydantic usually main fields.
                     # Document has metadata field?
                     metadata = getattr(result, 'metadata', {})
                 
                 if hasattr(metadata, 'dict'):
                     metadata = metadata.dict()
                 elif hasattr(metadata, 'model_dump'):
                     metadata = metadata.model_dump()
                 
                 # Fallbacks
                 if not isinstance(metadata, dict):
                     metadata = {}

                 title = metadata.get('title', 'Unknown Title')
                 source_url = metadata.get('sourceURL', url)
                 
                 normalized_url = normalize_url(source_url)
                 content_hash = compute_content_hash(content)
                 
                 doc_record = {
                     'url': source_url,
                     'url_normalized': normalized_url,
                     'title': title,
                     'content_text': content,
                     'content_hash': content_hash,
                     'extracted_date': datetime.now().isoformat(),
                     'source_type': source_type,
                     'county': county
                 }
                 
                 # Insert into DB
                 doc_id = crud.insert_raw_document(doc_record)
                 if doc_id != -1:
                     new_doc_ids.append(doc_id)
            
            # Be polite
            time.sleep(1)
            
        return new_doc_ids

if __name__ == "__main__":
    c = Collector()
    ids = c.run()
    print(f"Collected {len(ids)} documents.")
