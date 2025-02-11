import os
import uuid
import cv2 as cv

from src.configuration.Logger import Logger as log
from src.pinecone.PineconeWorker import PineconeWorker
from src.pinecone.PineconeManager import PineconeManager

VIDEO_STORE_LOCATION = os.environ["VIDEO_STORE_LOCATION"]
IMAGE_STORE_LOCATION = os.environ["IMAGE_STORE_LOCATION"]


class VideoManager:
    def slice_to_frames(self, video_name):
        frames = []
        video = cv.VideoCapture(os.path.join(VIDEO_STORE_LOCATION, video_name))
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

pm = PineconeManager()
vm = VideoManager()
# frames = vm.slice_to_frames("butterflies_960p.mp4")
#
# print(frames)
# for frame in frames:
#     vector = PineconeWorker.process_frame(frame)
#     PineconeManager.upsert_data(uuid.uuid4().__str__(), vector)

vector = PineconeWorker.process_frame(f"D:\\University\\Masters\\Thesis\\resources\\frames\\frame0.jpg")
print(PineconeManager.get_similar_data(vector))