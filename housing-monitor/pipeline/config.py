import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '../.env'))

# API Keys
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# DB & Vector Store
# DB & Vector Store
PROJECT_ROOT = os.path.join(os.path.dirname(__file__), '..')
_sqlite_env = os.getenv("SQLITE_PATH")
if _sqlite_env:
    if os.path.isabs(_sqlite_env):
        SQLITE_PATH = _sqlite_env
    else:
        # Resolve relative to project root, not CWD
        SQLITE_PATH = os.path.abspath(os.path.join(PROJECT_ROOT, _sqlite_env))
else:
    SQLITE_PATH = os.path.abspath(os.path.join(PROJECT_ROOT, 'data/app.db'))
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")

# Pipeline Settings
RELEVANCE_THRESHOLD = float(os.getenv("RELEVANCE_THRESHOLD", "0.70"))
DEDUPE_SIM_THRESHOLD = float(os.getenv("DEDUPE_SIM_THRESHOLD", "0.90"))
SCRAPE_MAX_PAGES_PER_SOURCE = int(os.getenv("SCRAPE_MAX_PAGES_PER_SOURCE", "30"))

# Sources (ONLY for now, would be in a YAML or DB)
SOURCES = [
    {
        "county": "Los Angeles",
        "source_type": "agenda",
        "url": "https://bos.lacounty.gov/board-meeting-agendas/"
    },
    {
        "county": "San Francisco",
        "source_type": "news",
        "url": "https://www.sf.gov/topics/housing"
    },
    {
        "county": "Adelanto",
        "source_type": "official",
        "url": "https://www.ci.adelanto.ca.us/"
    },
    {
        "county": "Agoura Hills",
        "source_type": "official",
        "url": "http://www.agourahillscity.org/"
    },
    {
        "county": "Alameda",
        "source_type": "official",
        "url": "https://www.alamedaca.gov/"
    },
    {
        "county": "Albany",
        "source_type": "official",
        "url": "http://www.albanyca.org/"
    },
    {
        "county": "Alhambra",
        "source_type": "official",
        "url": "http://www.cityofalhambra.org/"
    },
    {
        "county": "Aliso Viejo",
        "source_type": "official",
        "url": "http://www.cityofalisoviejo.com/"
    },
    {
        "county": "Alturas",
        "source_type": "official",
        "url": "http://www.cityofalturas.org/"
    },
    {
        "county": "Amador City",
        "source_type": "official",
        "url": "http://www.amador-city.com/"
    },
    {
        "county": "American Canyon",
        "source_type": "official",
        "url": "http://www.cityofamericancanyon.org/"
    },
    {
        "county": "Anaheim",
        "source_type": "official",
        "url": "http://www.anaheim.net/"
    }
    # Add more seed sources here
]
