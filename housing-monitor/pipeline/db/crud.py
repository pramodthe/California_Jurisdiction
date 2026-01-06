import sqlite3
import json
import logging
from typing import Dict, Any, List, Optional
from pipeline.config import SQLITE_PATH

logger = logging.getLogger(__name__)

def get_db_connection():
    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def insert_raw_document(doc: Dict[str, Any]) -> int:
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute('''
            INSERT OR IGNORE INTO raw_documents 
            (url, url_normalized, title, content_text, content_hash, extracted_date, source_type, county)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            doc['url'],
            doc['url_normalized'],
            doc.get('title'),
            doc.get('content_text'),
            doc.get('content_hash'),
            doc.get('extracted_date'),
            doc.get('source_type'),
            doc.get('county')
        ))
        conn.commit()
        # Get ID (if ignored, we might need to fetch it, but usually we just skip processing)
        if c.rowcount == 0:
            # It existed
            c.execute('SELECT id FROM raw_documents WHERE url_normalized = ?', (doc['url_normalized'],))
            row = c.fetchone()
            return row['id']
        return c.lastrowid
    except Exception as e:
        logger.error(f"Error inserting raw document: {e}")
        return -1
    finally:
        conn.close()

def insert_processed_item(item: Dict[str, Any]) -> int:
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute('''
            INSERT INTO items 
            (raw_document_id, title, summary, heading, key_points, impacted_parties, important_dates, 
             source_link, date_posted, ai_confidence, is_relevant, relevance_score, relevance_rationale, 
             topics, is_new, dedup_reason, matched_item_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            item.get('raw_document_id'),
            item.get('title'),
            item.get('summary'),
            item.get('heading'),
            json.dumps(item.get('key_points', [])),
            json.dumps(item.get('impacted_parties', [])),
            json.dumps(item.get('important_dates', [])),
            item.get('source_link'),
            item.get('date_posted'),
            item.get('ai_confidence'),
            item.get('is_relevant'),
            item.get('relevance_score'),
            item.get('relevance_rationale'),
            json.dumps(item.get('topics', [])),
            item.get('is_new'),
            item.get('dedup_reason'),
            item.get('matched_item_id')
        ))
        conn.commit()
        return c.lastrowid
    except Exception as e:
        logger.error(f"Error inserting processed item: {e}")
        return -1
    finally:
        conn.close()

def log_run(status: str, stats: Dict[str, Any]):
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute('''
            INSERT INTO runs (status, items_processed, items_relevant, items_new, error_log)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            status,
            stats.get('items_processed', 0),
            stats.get('items_relevant', 0),
            stats.get('items_new', 0),
            stats.get('error_log', '')
        ))
        conn.commit()
    except Exception as e:
        logger.error(f"Error logging run: {e}")
    finally:
        conn.close()
        
def get_latest_items(limit: int = 20, relevant_only: bool = True):
    conn = get_db_connection()
    c = conn.cursor()
    # Join with raw_documents to get source info like county
    query = """
        SELECT i.*, r.county 
        FROM items i
        LEFT JOIN raw_documents r ON i.raw_document_id = r.id
    """
    
    if relevant_only:
        query += " WHERE i.is_relevant = 1"
    
    query += " ORDER BY i.processed_at DESC LIMIT ?"
    
    c.execute(query, (limit,))
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]
