import argparse

from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

from src.config import COLLECTION_NAME, EMBEDDING_MODEL, QDRANT_URL


def parse_args():
    parser = argparse.ArgumentParser(description="Search the Qdrant knowledge base.")
    parser.add_argument("--limit", type=int, default=3, help="Number of search results to return.")
    parser.add_argument("--query", help="Run a single query and exit.")
    return parser.parse_args()


def print_hits(hits):
    for i, hit in enumerate(hits):
        score = hit.score
        payload = hit.payload

        print('-'*20)
        print(f'Result {i + 1}  | Score: {score:.4f}')
        print(f"Source: {payload['title']}")
        print(f"URL: {payload['url']}")
        print(f"Content: {payload['text'][:300]}...")
        print('-'*20)


def run_query(client, model, query, limit):
    query_vector = model.encode(query).tolist()

    return client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=limit,
        with_payload=True
    ).points


def search_knowledge_base(limit=3, query=None):
    print(f"Loading embedding model {EMBEDDING_MODEL}")
    model = SentenceTransformer(EMBEDDING_MODEL)

    print(f'Connecting to Qdrant at {QDRANT_URL}...')
    client = QdrantClient(url=QDRANT_URL)

    print("RAG system ready!")
    print("Type 'exit' to exit\n")

    if query:
        hits = run_query(client, model, query, limit)
        print_hits(hits)
        return

    while True:
        query = input("\n\nInput your question:\n")
        if query.lower() in ['exit', 'quit']:
            break
            
        hits = run_query(client, model, query, limit)
        print_hits(hits)

if __name__ == '__main__':
    args = parse_args()
    search_knowledge_base(limit=args.limit, query=args.query)
