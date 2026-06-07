"""
Main controller script for the RAG pipeline.
Orchestrates data fetching, processing, and vectorization.
"""
import argparse
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.raw_data import fetch_data
from src.process_data import process_chunks
from src.vectorize_db import load_to_qdrant


def parse_args():
    parser = argparse.ArgumentParser(description="Run the Dev.to RAG ingestion pipeline.")
    parser.add_argument("--tag", default="ai", help="Dev.to tag to fetch articles from.")
    parser.add_argument("--limit", type=int, default=20, help="Maximum number of articles to fetch.")
    parser.add_argument("--skip-fetch", action="store_true", help="Skip fetching raw articles.")
    parser.add_argument("--skip-process", action="store_true", help="Skip chunking raw articles.")
    parser.add_argument("--skip-vectorize", action="store_true", help="Skip embedding and Qdrant upload.")
    return parser.parse_args()


def run_pipeline(tag="ai", limit=20, skip_fetch=False, skip_process=False, skip_vectorize=False):
    """
    Run the complete RAG pipeline.
    
    Args:
        tag: Tag to fetch articles from dev.to
        limit: Maximum number of articles to fetch
        skip_fetch: Skip data fetching step
        skip_process: Skip data processing step
        skip_vectorize: Skip vectorization step
    """
    print("=" * 60)
    print("Starting RAG Pipeline")
    print("=" * 60)
    
    try:
        # Step 1: Fetch raw data
        if not skip_fetch:
            print("\n[Step 1/3] Fetching raw data from dev.to...")
            fetch_data(tag=tag, limit=limit)
        else:
            print("\n[Step 1/3] Skipping data fetch...")
        
        # Step 2: Process and chunk data
        if not skip_process:
            print("\n[Step 2/3] Processing and chunking data...")
            process_chunks()
        else:
            print("\n[Step 2/3] Skipping data processing...")
        
        # Step 3: Vectorize and load to Qdrant
        if not skip_vectorize:
            print("\n[Step 3/3] Vectorizing and loading to Qdrant...")
            load_to_qdrant()
        else:
            print("\n[Step 3/3] Skipping vectorization...")
        
        print("\n" + "=" * 60)
        print("Pipeline completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nPipeline failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    args = parse_args()
    run_pipeline(
        tag=args.tag,
        limit=args.limit,
        skip_fetch=args.skip_fetch,
        skip_process=args.skip_process,
        skip_vectorize=args.skip_vectorize,
    )
