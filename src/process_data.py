import json
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config import PROCESSED_CHUNKS_FILE, PROCESSED_DATA_DIR, RAW_DATA_FILE

PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

def process_chunks():
    if not RAW_DATA_FILE.exists():
        print(f"Cannot open {RAW_DATA_FILE} to process chunks")
        return

    with open(RAW_DATA_FILE, 'r', encoding='utf-8') as file:
        articles = json.load(file)

    print(f"Processing {len(articles)} articles...")

    # Analyze spliter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 1000,
        chunk_overlap = 200,
        separators=["\n\n", "\n", " ", ""]
    )

    all_chunks = []

    for article in articles:
        markdown_content = article.get('content', {}).get('markdown', '')

        if not markdown_content:
            continue
        
        chunks = text_splitter.create_documents([markdown_content])

        for chunk in chunks:
            metadata = dict(article['metadata'])
            metadata['chunk_len'] = len(chunk.page_content)

            chunk_record = {
                "text": chunk.page_content,
                "metadata": metadata,
                "article_id": article['id']
            }

            all_chunks.append(chunk_record)

    with open(PROCESSED_CHUNKS_FILE, 'w', encoding='utf-8') as file:
        json.dump(all_chunks, file, ensure_ascii=False, indent=2)

    print('Chunking raw data done')
    print(f'From {len(articles)} articles created {len(all_chunks)} chunks')

if __name__ == "__main__":
    process_chunks()
