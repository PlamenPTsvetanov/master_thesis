import json
import os
import uuid

import cv2 as cv

from src.configuration.Logger import Logger as log
from src.kafka.VideoStatusKafkaProducer import VideoStatusKafkaProducer
from src.pinecone.PineconeManager import PineconeManager
from src.pinecone.PineconeWorker import PineconeWorker

IMAGE_STORE_LOCATION = os.environ["IMAGE_STORE_LOCATION"]

pinecone_worker = PineconeWorker()
pinecone_manager = PineconeManager()


class VideoManager:
    @staticmethod
    def slice_to_frames(video_location):
        frames = []
        video = cv.VideoCapture(video_location)
        read, image = video.read()
        count = 0
        while read:
            path = os.path.join(IMAGE_STORE_LOCATION, f"frame{count}.jpg")
            cv.imwrite(path, image)
            success, image = video.read()
            log.debug(f"Read frame #{count}")

            frames.append(path)
            count += 1

            if count > 5:
                break

        return frames

    def process_video_created(self, input_video_meta):
        try:
            frames = self.slice_to_frames(input_video_meta["location"])

            vectors = []
            for frame in frames:
                vector = pinecone_worker.process_frame(frame)
                vectors.append({"vector": vector, "id": input_video_meta["databaseId"]})

            for i in range(0, len(vectors), 6):
                vector = vectors[i]
                similarities = pinecone_manager.get_similar_data(vector["vector"])
                similarities = [match.score for match in similarities.matches if match.score > 0.90]

                if len(similarities) > 1:
                    VideoStatusKafkaProducer.produce(
                        json.dumps({"id": vector["id"], "message": "Similarity score too high! Possible duplicate!"}))
                    raise Exception("Similarity score too high! Possible duplicate!")

            for vector in vectors:
                self.add_new_video(input_video_meta, vector)
        except Exception as e:
            print(e)

    @staticmethod
    def add_new_video(input_video_meta, vector):
        meta = {"database_id": input_video_meta["databaseId"]}
        pinecone_manager.upsert_data(uuid.uuid4().__str__(), vector, meta)
