import os
import time
from pinecone import Pinecone, ServerlessSpec

PINECONE_API_KEY = os.environ['PINECONE_API_KEY']
pc = Pinecone(api_key=PINECONE_API_KEY)
index_name = 'image-similarity'


class PineconeManager:

    def __init__(self):
        if index_name not in pc.list_indexes().names():
            pc.create_index(name=index_name, dimension=2048, metric="cosine",
                            spec=ServerlessSpec(cloud="aws", region="us-east-1"))

    def upsert_data(self, image_id, data):
        while not pc.describe_index(index_name).status['ready']:
            time.sleep(1)
        index = pc.Index(index_name)

        vector = [{
            'id': image_id,
            'values': data,
        }]
        index.upsert(vector)

    def get_similar_data(self, data):
        index = pc.Index(index_name)
        results = index.query(
            namespace="ns1",
            vector=data,
            top_k=5,
            include_values=False,
            include_metadata=True
        )
        return results
