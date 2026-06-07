import argparse

from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
import google.genai as genai
from dotenv import load_dotenv
import os

from src.config import COLLECTION_NAME, EMBEDDING_MODEL, QDRANT_URL

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

gemini_client = genai.Client(api_key=GEMINI_API_KEY)


def parse_args():
    parser = argparse.ArgumentParser(description="Search the Qdrant knowledge base and answer with Gemini.")
    parser.add_argument("--limit", type=int, default=3, help="Number of retrieved chunks to send to Gemini.")
    parser.add_argument("--query", help="Run a single query and exit.")
    parser.add_argument("--model", default="gemini-2.5-flash", help="Gemini model name.")
    return parser.parse_args()


def build_prompt(query, context_text):
    return f"""
    You are a helpful and knowledgeable software engineering assistant.
    Your task is to answer the user's question using ONLY the provided context below.
    
    Instructions:
    1. Answer strictly based on the provided context.
    2. If the context does not contain the answer, explicitly state: "I cannot find the answer in the provided documents."
    3. Do not make up information or use outside knowledge unless necessary to explain the context.
    4. Answer in the same language as the user's question.

    ### Context:
    {context_text}

    ### User Question:
    {query}

    ### Answer:
    """


def run_query(client, embedder, query, limit):
    query_vector = embedder.encode(query).tolist()

    return client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=limit,
        with_payload=True
    ).points


def answer_query(client, embedder, query, limit, gemini_model):
    hits = run_query(client, embedder, query, limit)

    print(f"{len(hits)} info found")

    context_text = ""

    for hit in hits:
        payload = hit.payload
        title = payload.get('title', 'N/A')
        text = payload.get('text', '')
        context_text += f"\n---\nSource: {title}\nContent: {text}\n"
        
    print("Thinking...")

    prompt = build_prompt(query, context_text)

    try:
        response = gemini_client.models.generate_content(
            model=gemini_model,
            contents=prompt
        )
        print(f"\nAssistance: {response.text}")
        print('-'*30)
    except Exception as e:
        print(f"Error calling Gemini API: {e}")


def search_knowledge_base(limit=3, query=None, gemini_model="gemini-2.5-flash"):
    print(f"Loading embedding model {EMBEDDING_MODEL}")
    model = SentenceTransformer(EMBEDDING_MODEL)

    print(f'Connecting to Qdrant at {QDRANT_URL}...')
    client = QdrantClient(url=QDRANT_URL, check_compatibility=False)

    print("RAG system ready!")
    print("Type 'exit' to exit\n")

    if query:
        answer_query(client, model, query, limit, gemini_model)
        return

    while True:
        query = input("\n\nInput your question:\n")
        if query.lower() in ['exit', 'quit']:
            break
        answer_query(client, model, query, limit, gemini_model)


if __name__ == '__main__':
    args = parse_args()
    search_knowledge_base(limit=args.limit, query=args.query, gemini_model=args.model)
