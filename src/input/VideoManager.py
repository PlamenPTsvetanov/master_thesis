import json
import os
import uuid
import numpy as np
import cv2 as cv
from PIL import Image

from src.configuration.Logger import Logger as log
from src.kafka.VideoStatusKafkaProducer import VideoStatusKafkaProducer
from src.pinecone.PineconeManager import PineconeManager
from src.pinecone.PineconeWorker import PineconeWorker

IMAGE_STORE_LOCATION = os.environ["IMAGE_STORE_LOCATION"]

face_cascade = cv.CascadeClassifier('/app/src/input/haarcascade_frontalface_default.xml')

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
        deepfake_status = "NO_DEEPFAKE"
        deepfake_message = ""
        try:
            frames = self.slice_to_frames(input_video_meta["location"])

            vectors = []
            for frame in frames:
                deepfake_status, deepfake_message = self.manage_deepfake_detection(frame)
                vector = pinecone_worker.process_frame(frame)
                vectors.append({"vector": vector, "id": input_video_meta["databaseId"]})

            video_uploaded = False
            for i in range(0, len(vectors), 3):
                vector = vectors[i]
                similarities = pinecone_manager.get_similar_data(vector["vector"])
                filtered = [match for match in similarities.matches]
                similarities = [match.score for match in similarities.matches if match.score > 0.90]

                if len(similarities) > 0:
                    video_uploaded = True
                    match = filtered[0]
                    if input_video_meta["userEmail"] == match.metadata.get("user_email"):
                        status = "REUPLOAD"
                        message = "Video already uploaded by this user!"
                    else:
                        if match.metadata.get('free_to_use') and match.metadata.get('is_copyrighted'):
                            if match.metadata.get('user_email') in input_video_meta['description']:
                                status = "VALID_REFERENCE"
                                message = "Video is copyrighted, but contains valid reference."
                            else:
                                status = "INVALID_REFERENCE"
                                message = "Video is copyrighted, but does not contain a valid reference."
                        elif match.metadata.get('free_to_use'):
                            status = "FREE_TO_USE"
                            message = "Found similar video, but it's free to use."
                        elif match.metadata.get('is_copyrighted'):
                            if len(vectors) > 4500:
                                status = "COPYRIGHT"
                                message = "Copyrighted content which doesn't fall into fair use."
                            else:
                                status = "FAIR_USE_COPYRIGHT"
                                message = "Uploading copyrighted content that falls into fair use."
                        else:  # не е free_to_use и не е copyrighted
                            status = "EXCEPTION"
                            message = "Similarity score too high with non free-use video! Possible duplicate!"

            print(f"{video_uploaded}, {status}, {message}")
            if not video_uploaded:
                for vector in vectors:
                    self.add_new_video(input_video_meta, vector['vector'])

            VideoStatusKafkaProducer.produce(
                json.dumps({"id": input_video_meta["databaseId"], "status": status,
                            "message": message, "deepfakeStatus": deepfake_status, "deepfakeMessage": deepfake_message}),)
        except Exception as e:
            print(e)

    def manage_deepfake_detection(self, frame):
        deepfake_status = "NO_DEEPFAKE"
        deepfake_message = ""
        found_faces = self.find_faces_crops(frame)
        if len(found_faces) > 0:
            deepfake_found = False
            # send for deepfake detection
            if deepfake_found:
                deepfake_status = "DEEPFAKE_FOUND"
                deepfake_message = "Found deepfake content!"
        else:
            deepfake_message = "No faces found!"
        return deepfake_status, deepfake_message

    @staticmethod
    def find_faces_crops(image_path):
        img_pil = Image.open(image_path)
        img = np.array(img_pil)
        img = cv.cvtColor(img, cv.COLOR_RGB2BGR)

        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(gray, 1.1, 8)
        face_crops = []
        if len(faces) > 0:
            max_face_size = max([w for (x, y, w, h) in faces])

            for (x, y, w, h) in faces:
                k = 0.3
                pad = int(k * (max_face_size / w) * w)

                x_pad = max(x - pad, 0)
                y_pad = max(y - pad, 0)
                w_pad = min(w + 2 * pad, img.shape[1] - x_pad)
                h_pad = min(h + 2 * pad, img.shape[0] - y_pad)

                face_crops.append(img[y_pad:y_pad + h_pad, x_pad:x_pad + w_pad])
        return face_crops
    @staticmethod
    def add_new_video(input_video_meta, vector):
        meta = {"database_id": input_video_meta["databaseId"],
                "free_to_use": input_video_meta["freeToUse"],
                "is_copyrighted": input_video_meta["isCopyrighted"],
                "user_email": input_video_meta["userEmail"],
                "description": input_video_meta["description"],
                }
        id_with_parent = input_video_meta["databaseId"] + "#" + str(uuid.uuid4())
        pinecone_manager.upsert_data(id_with_parent, vector, meta)
