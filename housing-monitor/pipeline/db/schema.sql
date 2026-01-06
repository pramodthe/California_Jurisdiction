CREATE TABLE IF NOT EXISTS raw_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL,
    url_normalized TEXT UNIQUE NOT NULL,
    title TEXT,
    content_text TEXT,
    content_hash TEXT,
    scraped_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    extracted_date TEXT,
    source_type TEXT,
    county TEXT
);

CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    raw_document_id INTEGER,
    title TEXT,
    summary TEXT,
    heading TEXT,
    key_points TEXT, -- JSON array
    impacted_parties TEXT, -- JSON array
    important_dates TEXT, -- JSON array
    source_link TEXT,
    date_posted TEXT,
    ai_confidence REAL,
    is_relevant BOOLEAN,
    relevance_score REAL,
    relevance_rationale TEXT, -- max 40 words
    topics TEXT, -- JSON array
    is_new BOOLEAN,
    dedup_reason TEXT,
    matched_item_id INTEGER,
    processed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(raw_document_id) REFERENCES raw_documents(id)
);

CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status TEXT, -- 'success', 'failed'
    items_processed INTEGER,
    items_relevant INTEGER,
    items_new INTEGER,
    error_log TEXT
);
