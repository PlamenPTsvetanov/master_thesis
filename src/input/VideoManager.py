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
        status = "COMPLETED"
        message = "Successfully added video!"
        try:
            frames = self.slice_to_frames(input_video_meta["location"])

            vectors = []
            for frame in frames:
                vector = pinecone_worker.process_frame(frame)
                vectors.append({"vector": vector, "id": input_video_meta["databaseId"]})

            upload_video = True
            for i in range(0, len(vectors), 3):
                vector = vectors[i]
                similarities = pinecone_manager.get_similar_data(vector["vector"])
                filtered = [match for match in similarities.matches]
                similarities = [match.score for match in similarities.matches if match.score > 0.90]

                match = filtered[0]

                if input_video_meta["userId"] == match.metadata.get("userId"):
                    status = "REUPLOAD"
                    message = "Video already uploaded by this user!"
                    upload_video = False
                elif len(similarities) > 0:
                    if match.metadata.get('free_to_use') and match.metadata.get('is_copyrighted'):
                        if input_video_meta['description'].contains[match.metadata.get('free_to_use')]:
                            status = "VALID_REFERENCE"
                            message = "Video is copyrighted, but contains valid reference."
                        else:
                            status = "INVALID_REFERENCE"
                            message = "Video is copyrighted, but does not contain a valid reference."
                            upload_video = False
                    elif match.metadata.get('free_to_use'):
                        status = "FREE_TO_USE"
                        message = "Found similar video, but it's free to use."
                    elif match.metadata.get('is_copyrighted'):
                        status = "COPYRIGHTED"
                        if len(vectors) > 4500:
                            message = "Copyrighted content which doesn't fall inyo fair use."
                            upload_video = False
                        else:
                            message = "Uploading copyrighted content that falls into fair use."
                    else:
                        status = "EXCEPTION"
                        message = "Similarity score too high! Possible duplicate!"
                        upload_video = False

            if upload_video:
                for vector in vectors:
                    self.add_new_video(input_video_meta, vector['vector'])

            VideoStatusKafkaProducer.produce(
                json.dumps({"id": input_video_meta["databaseId"], "status": status,
                            "message": message}))
        except Exception as e:
            print(e)

    @staticmethod
    def add_new_video(input_video_meta, vector):
        meta = {"database_id": input_video_meta["databaseId"],
                "free_to_use": input_video_meta["freeToUse"],
                "is_copyrighted": input_video_meta["isCopyrighted"]
                }
        id_with_parent = input_video_meta["databaseId"] + "#" + str(uuid.uuid4())
        pinecone_manager.upsert_data(id_with_parent, vector, meta)
