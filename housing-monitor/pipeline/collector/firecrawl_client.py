# pipeline/collector/firecrawl_client.py
import os
from firecrawl import FirecrawlApp
from pipeline.config import FIRECRAWL_API_KEY

class FirecrawlClient:
    def __init__(self, mock: bool = False):
        self.api_key = FIRECRAWL_API_KEY
        self.mock = mock
        if self.api_key and not self.mock:
             self.app = FirecrawlApp(api_key=self.api_key)
        else:
            self.app = None

    def scrape_url(self, url: str):
        if not self.app:
            # Mock response
            return {
                "markdown": f"# Housing Legislation Update for {url}\n\n## Rent Control Ordinance\n\nThe Board has proposed a new ordinance to limit rent increases to 3% annually. This measure aims to protect tenants from displacement.\n\n### Key Details\n- **Cap**: 3% per year.\n- **Effective Date**: January 1st, 2026.\n- **Exemptions**: New construction within 15 years.\n\nResidents are encouraged to attend the upcoming hearing to voice their opinions.",
                "metadata": {"title": "Rent Stabilization Ordinance Proposal", "sourceURL": url}
            }
        
        try:
            # firecrawl-py v4+ uses scrape(url, formats=['markdown'])
            scrape_result = self.app.scrape(url, formats=['markdown'])
            return scrape_result
        except Exception as e:
            print(f"Firecrawl error: {e}")
            return None
