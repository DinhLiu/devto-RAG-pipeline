# Dev.to RAG Pipeline

A compact Retrieval-Augmented Generation pipeline for collecting Dev.to articles, chunking them, embedding the chunks, storing them in Qdrant, and querying them through either semantic search or Gemini.

## What It Does

- Fetches Dev.to articles by tag.
- Converts article HTML to Markdown.
- Splits article content into searchable chunks.
- Creates embeddings with `sentence-transformers/all-MiniLM-L6-v2`.
- Stores vectors and metadata in Qdrant.
- Supports basic semantic search from Qdrant.
- Supports Gemini-powered answers using retrieved context.

## Requirements

- Python 3.8+
- Docker or Docker Desktop
- A Gemini API key, only if you want to use `src.search_gemini`

## Setup

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Create a `.env` file for Gemini search:

```text
GEMINI_API_KEY=YOUR_KEY
```

Start Qdrant:

```powershell
docker compose up -d
```

Qdrant dashboard:

```text
http://localhost:6333/dashboard
```

## Quick Start

Fetch articles, process chunks, and upload vectors to Qdrant:

```powershell
python -m scripts.pipeline --tag programming --limit 100
```

Run basic semantic search:

```powershell
python -m src.search_basic --query "What is RAG?" --limit 5
```

Run Gemini RAG search:

```powershell
python -m src.search_gemini --query "What is RAG?" --limit 5 --model gemini-2.5-flash
```

## Commands

### Pipeline

Run the full pipeline:

```powershell
python -m scripts.pipeline --tag programming --limit 100
```

Use existing raw data and regenerate processed chunks plus Qdrant vectors:

```powershell
python -m scripts.pipeline --skip-fetch
```

Use existing processed chunks and only upload vectors to Qdrant:

```powershell
python -m scripts.pipeline --skip-fetch --skip-process
```

Fetch and process articles without uploading vectors:

```powershell
python -m scripts.pipeline --tag python --limit 50 --skip-vectorize
```

Arguments:

```text
python -m scripts.pipeline [--tag TAG] [--limit LIMIT] [--skip-fetch] [--skip-process] [--skip-vectorize]
```

### Tag Crawler

Fetch Dev.to tags into the default tag file:

```powershell
python -m scripts.tag_crawler
```

Write tags to a custom file:

```powershell
python -m scripts.tag_crawler --output data/tags/devto_tags.txt
```

Arguments:

```text
python -m scripts.tag_crawler [--output PATH]
```

### Basic Search

Start interactive search:

```powershell
python -m src.search_basic --limit 5
```

Run one query and exit:

```powershell
python -m src.search_basic --query "What is RAG?" --limit 5
```

Arguments:

```text
python -m src.search_basic [--limit LIMIT] [--query QUERY]
```

### Gemini Search

Start interactive Gemini search:

```powershell
python -m src.search_gemini --limit 5
```

Run one Gemini query and exit:

```powershell
python -m src.search_gemini --query "What is RAG?" --limit 5 --model gemini-2.5-flash
```

Arguments:

```text
python -m src.search_gemini [--limit LIMIT] [--query QUERY] [--model MODEL]
```

## Project Structure

```text
devto-RAG-pipeline/
|-- data/
|   |-- processed/          # Generated chunk JSON files
|   |-- raw/                # Generated raw article JSON files
|   `-- tags/               # Generated tag list files
|-- qdrant_storage/         # Qdrant persistent storage
|-- scripts/
|   |-- pipeline.py         # Pipeline CLI entrypoint
|   `-- tag_crawler.py      # Dev.to tag crawler CLI
|-- src/
|   |-- config.py           # Shared paths and service settings
|   |-- process_data.py     # Chunking logic
|   |-- raw_data.py         # Article fetching logic
|   |-- search_basic.py     # Basic Qdrant search CLI
|   |-- search_gemini.py    # Gemini RAG search CLI
|   `-- vectorize_db.py     # Embedding and Qdrant upload logic
|-- docker-compose.yaml
|-- requirements.txt
`-- readme.md
```

## Runtime Paths

Runtime paths are centralized in `src/config.py`:

```text
data/raw/raw_data.json
data/processed/processed_chunks.json
data/tags/tag_list.txt
```

The generated data directories are ignored by Git.

## Notes

- Run commands from the repository root.
- Start Qdrant before running vector upload or search commands.
- Large vector uploads are batched before sending to Qdrant to avoid oversized HTTP payloads.
- Gemini search requires `GEMINI_API_KEY` in `.env`.
