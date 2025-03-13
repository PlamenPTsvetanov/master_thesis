import os
import time
import torch
from pinecone import Pinecone, ServerlessSpec
import json

PINECONE_API_KEY = os.environ['PINECONE_API_KEY']
pc = Pinecone(api_key=PINECONE_API_KEY)
index_name = 'image-similarity'


class PineconeManager:

    def __init__(self):
        if index_name not in pc.list_indexes().names():
            pc.create_index(name=index_name, dimension=2048, metric="cosine",
                            spec=ServerlessSpec(cloud="aws", region="us-east-1"))

    @staticmethod
    def upsert_data(image_id, data, meta):
        while not pc.describe_index(index_name).status['ready']:
            time.sleep(1)
        index = pc.Index(index_name)

        vector = [{
            'id': image_id,
            'values': data,
            "metadata": meta
        }]
        index.upsert(vector)

    @staticmethod
    def delete_data(prefix):
        index = pc.Index(host="https://image-similarity-khlazmd.svc.aped-4627-b74a.pinecone.io")
        for ids in index.list(prefix=prefix):
            index.delete(ids=ids)

    @staticmethod
    def get_similar_data(data):
        if isinstance(data, torch.Tensor):
            data = data.cpu().numpy().tolist()

        index = pc.Index(index_name)
        results = index.query(
            vector=data,
            top_k=9001, # 5 minutes 30 frames
            include_values=False,
            include_metadata=True
        )
        return results
