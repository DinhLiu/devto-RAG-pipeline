from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
TAGS_DATA_DIR = DATA_DIR / "tags"

RAW_DATA_FILE = RAW_DATA_DIR / "raw_data.json"
PROCESSED_CHUNKS_FILE = PROCESSED_DATA_DIR / "processed_chunks.json"
TAG_LIST_FILE = TAGS_DATA_DIR / "tag_list.txt"

COLLECTION_NAME = "devto_articles"
QDRANT_URL = "http://localhost:6333"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
