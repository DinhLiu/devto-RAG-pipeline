import json
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
import uuid

from src.config import COLLECTION_NAME, EMBEDDING_MODEL, PROCESSED_CHUNKS_FILE, QDRANT_URL

BATCH_SIZE = 64


def upsert_batch(client, points, uploaded_count, total_count):
    if not points:
        return uploaded_count

    client.upsert(collection_name=COLLECTION_NAME, points=points)
    uploaded_count += len(points)
    print(f'Uploaded {uploaded_count}/{total_count} chunks')
    return uploaded_count


def load_to_qdrant():

    # Initialyze Model and Client
    print(f"Loading embedding model {EMBEDDING_MODEL}...")
    encoder = SentenceTransformer(EMBEDDING_MODEL)

    print(f"Connecting to Qdrant at {QDRANT_URL}")
    client = QdrantClient(url=QDRANT_URL)

    # Create Collection
    if not client.collection_exists(COLLECTION_NAME):
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE)
        )
        print(f"Collection {COLLECTION_NAME} created sucessfully")
    else:
        print(f"Collection {COLLECTION_NAME} has already been exist")

    try:
        with open(PROCESSED_CHUNKS_FILE, 'r', encoding='utf-8') as file:
            chunks = json.load(file)
    except FileNotFoundError:
        print(f'Cannot find file {PROCESSED_CHUNKS_FILE}')
        return
    
    print(f"Start adding {len(chunks)} chunks into database...")

    points = []
    uploaded_count = 0

    for idx, chunk in enumerate(chunks):
        text = chunk['text']
        metadata = chunk['metadata']
        article_id = chunk['article_id']

        # EMbedding: convert text into vectors
        vector = encoder.encode(text).tolist()

        # Pack into point (data point)
        point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{article_id}_{idx}"))

        # Payload
        payload = dict(metadata)
        payload['text'] = text
        payload['article_id'] = article_id

        points.append(PointStruct(id=point_id, vector=vector, payload=payload))

        if len(points) >= BATCH_SIZE:
            uploaded_count = upsert_batch(client, points, uploaded_count, len(chunks))
            points = []

    uploaded_count = upsert_batch(client, points, uploaded_count, len(chunks))

    print(f"Vectorize done")

if __name__ == "__main__":
    load_to_qdrant()
