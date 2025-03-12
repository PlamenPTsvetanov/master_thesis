import os
import uuid

from confluent_kafka import Producer
from src.configuration.Logger import Logger
from src.kafka.KafkaAdmin import KafkaAdmin

BOOTSTRAP_SERVER = os.environ['KAFKA_BOOTSTRAP_SERVERS']
KAFKA_CONFIG = {
    'bootstrap.servers': BOOTSTRAP_SERVER,
    'client.id': uuid.uuid4()
}

topic = "video.status"
producer = Producer(KAFKA_CONFIG)


class VideoStatusKafkaProducer():
    @staticmethod
    def produce(message):
        Logger.info("Producing message to Kafka topic")
        KafkaAdmin.create_if_not_exists(topic_name=topic)
        producer.produce(topic=topic, key=str(uuid.uuid4()), value=message)
