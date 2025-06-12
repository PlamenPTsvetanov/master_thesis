import os

from confluent_kafka import Consumer

from src.kafka.KafkaAdmin import KafkaAdmin
from src.pinecone.PineconeManager import PineconeManager
from src.configuration.Logger import Logger

BOOTSTRAP_SERVER = os.environ['KAFKA_BOOTSTRAP_SERVERS']
KAFKA_CONFIG = {
    'bootstrap.servers': BOOTSTRAP_SERVER,
    'group.id': 'py-deleted',
    'auto.offset.reset': 'latest'
}
pinecone_manager = PineconeManager()


class VideoDeletedKafkaConsumer():

    @staticmethod
    def consume_messages(consumer):
        try:
            while True:
                msg = consumer.poll(timeout=1.0)
                if msg is None:
                    continue
                if msg.error():
                    Logger.warning(f"Consumer error: {msg.error()}")
                    continue

                Logger.info(f"Received message: {msg.value().decode('utf-8')}")
                video_id_delete = msg.value().decode('utf-8')
                pinecone_manager.delete_data(video_id_delete)
        finally:
            consumer.close()

    def run(self):
        Logger.info("Running video deletion consumer")
        consumer = Consumer(KAFKA_CONFIG)
        video_created_topic = 'video.deleted'
        video_created_topic = KafkaAdmin.create_if_not_exists(video_created_topic)

        consumer.subscribe([video_created_topic])
        self.consume_messages(consumer)
