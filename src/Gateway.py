import threading

from src.kafka.VideoCreatedKafkaConsumer import VideoCreatedKafkaConsumer
from src.kafka.VideoDeletedKafkaConsumer import VideoDeletedKafkaConsumer

VIDEO_CREATED_CONSUMER = VideoCreatedKafkaConsumer()
VIDEO_DELETED_CONSUMER = VideoDeletedKafkaConsumer()
if __name__ == "__main__":
    t_v_created_thread = threading.Thread(target=VIDEO_CREATED_CONSUMER.run, name="video_created_thread")
    t_v_deleted_thread = threading.Thread(target=VIDEO_DELETED_CONSUMER.run, name="video_deleted_thread")

    t_v_created_thread.daemon = True
    t_v_deleted_thread.daemon = True

    t_v_created_thread.start()
    t_v_deleted_thread.start()

    t_v_created_thread.join()
    t_v_deleted_thread.join()