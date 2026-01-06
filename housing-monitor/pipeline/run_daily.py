import logging
import sys
import os
import argparse

# Ensure we're running from proper directory context if needed, though imports handle it
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from pipeline.collector.collect import Collector
from pipeline.graph import app_graph
import pipeline.db.crud as crud
from pipeline.logger_config import setup_logging

logger = logging.getLogger(__name__)

def run_pipeline(mock: bool = False):
    logger.info(f"Starting Daily Run (Mock={mock})")
    
    # 1. Collect
    collector = Collector(mock=mock)
    new_doc_ids = collector.run()
    logger.info(f"Collector finished. {len(new_doc_ids)} new raw documents.")
    
    if not new_doc_ids:
        logger.info("No new documents to process.")
        return

    # 2. Process each new document through the graph
    conn = crud.get_db_connection()
    c = conn.cursor()
    
    stats = {
        "items_processed": 0,
        "items_relevant": 0,
        "items_new": 0,
        "error_log": ""
    }

    try:
        for doc_id in new_doc_ids:
            # Fetch full doc
            c.execute('SELECT * FROM raw_documents WHERE id = ?', (doc_id,))
            row = c.fetchone()
            if not row:
                continue
                
            doc_dict = dict(row)
            
            # Run Graph
            initial_state = {
                "raw_document_id": doc_id,
                "doc": doc_dict,
                "status": "pending"
            }
            
            try:
                final_state = app_graph.invoke(initial_state)
                final_doc = final_state['doc']
                
                stats["items_processed"] += 1
                if final_doc.get('is_relevant'):
                    stats["items_relevant"] += 1
                if final_doc.get('is_new'):
                    stats["items_new"] += 1
                    
            except Exception as e:
                logger.error(f"Error processing doc {doc_id}: {e}")
                stats["error_log"] += f"Doc {doc_id}: {str(e)}\n"
                
    except Exception as e:
        logger.error(f"Pipeline flow error: {e}")
        stats["error_log"] += f"Global: {str(e)}\n"
    finally:
        conn.close()
        
    # 3. Log Run
    crud.log_run("success", stats)
    logger.info(f"Run completed. Stats: {stats}")

if __name__ == "__main__":
    setup_logging()
    parser = argparse.ArgumentParser()
    parser.add_argument("--mock", action="store_true", help="Run with mock data if needed")
    args = parser.parse_args()
    
    run_pipeline(mock=args.mock)
