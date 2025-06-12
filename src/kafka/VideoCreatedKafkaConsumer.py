import json
import os

from confluent_kafka import Consumer

from src.input.VideoManager import VideoManager
from src.kafka.KafkaAdmin import KafkaAdmin
from src.configuration.Logger import Logger

BOOTSTRAP_SERVER = os.environ['KAFKA_BOOTSTRAP_SERVERS']
KAFKA_CONFIG = {
    'bootstrap.servers': BOOTSTRAP_SERVER,
    'group.id': 'py-created',
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
                    Logger.warning(f"Consumer problem: {msg.error()}")
                    continue

                Logger.info(f"Received message: {msg.value().decode('utf-8')}")
                video_created_json = json.loads(msg.value().decode('utf-8'))
                video_manager.process_video_created(video_created_json)
        finally:
            consumer.close()

    def run(self):
        Logger.info("Running video creation consumer")
        consumer = Consumer(KAFKA_CONFIG)
        video_created_topic = 'video.created'
        video_created_topic = KafkaAdmin.create_if_not_exists(video_created_topic)

        consumer.subscribe([video_created_topic])
        self.consume_messages(consumer)
