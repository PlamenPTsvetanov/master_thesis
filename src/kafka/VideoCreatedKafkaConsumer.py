import json
import os

from confluent_kafka import Consumer

from src.input.VideoManager import VideoManager
from src.kafka.KafkaAdmin import KafkaAdmin


BOOTSTRAP_SERVER = os.environ['KAFKA_BOOTSTRAP_SERVERS']
KAFKA_CONFIG = {
    'bootstrap.servers': BOOTSTRAP_SERVER,
    'group.id': 'dev',
    'auto.offset.reset': 'latest'
}
video_manager = VideoManager()


class VideoCreatedKafkaConsumer():

    @staticmethod
    def consume_messages(consumer):
        try:
            while True:
                msg = consumer.poll(timeout=1.0)
                if msg is None:
                    continue
                if msg.error():
                    print(f"Consumer error: {msg.error()}")
                    continue

                print(f"Received message: {msg.value().decode('utf-8')}")
                video_created_json = json.loads(msg.value().decode('utf-8'))
                video_manager.process_video_created(video_created_json)
        finally:
            consumer.close()

    def run(self):
        consumer = Consumer(KAFKA_CONFIG)
        video_created_topic = 'video.created'
        video_created_topic = KafkaAdmin.create_if_not_exists(video_created_topic)

        consumer.subscribe([video_created_topic])
        self.consume_messages(consumer)
