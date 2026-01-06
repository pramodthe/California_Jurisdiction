import hashlib
from urllib.parse import urlparse, urlunparse

def normalize_url(url: str) -> str:
    """
    Normalize URL by removing query parameters and extraction fragments,
    lowercasing scheme and netloc, and removing trailing slash.
    """
    parsed = urlparse(url)
    # Reconstruct without query/fragment
    clean_url = urlunparse((
        parsed.scheme.lower(),
        parsed.netloc.lower(),
        parsed.path.rstrip('/'),
        '', '', ''
    ))
    return clean_url

def compute_content_hash(content: str) -> str:
    """
    Compute a SHA-256 hash of the content for deduplication.
    """
    if not content:
        return ""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()
