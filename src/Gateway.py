import uuid

from src.input.VideoManager import VideoManager
from src.pinecone.PineconeManager import PineconeManager
from src.pinecone.PineconeWorker import PineconeWorker

video_manager = VideoManager()
pinecone_worker = PineconeWorker()
pinecone_manager = PineconeManager()


class Gateway:
    @staticmethod
    def process_video_created(video_name):
        frames = video_manager.slice_to_frames(video_name)

        for frame in frames:
            vector = pinecone_worker.process_frames(frame)
            pinecone_manager.upsert_data(uuid.uuid4(), vector)
