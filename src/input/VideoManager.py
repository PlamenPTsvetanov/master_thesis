import os

import cv2 as cv

from src.configuration.Logger import Logger as log

IMAGE_STORE_LOCATION = os.environ["IMAGE_STORE_LOCATION"]


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