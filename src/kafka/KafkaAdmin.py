import os

from confluent_kafka.admin import AdminClient
from confluent_kafka.cimpl import NewTopic

BOOTSTRAP_SERVER = os.environ['KAFKA_BOOTSTRAP_SERVERS']
KAFKA_CONFIG = {
    'bootstrap.servers': BOOTSTRAP_SERVER,
    'group.id': 'dev',
    'auto.offset.reset': 'latest'
}


class KafkaAdmin:
    @staticmethod
    def create_if_not_exists(topic_name):
        admin = AdminClient(KAFKA_CONFIG)
        metadata = admin.list_topics(timeout=10)
        if topic_name in metadata.topics:
            print(f"Topic '{topic_name}' exists.")
            return topic_name
        else:
            print(f"Topic '{topic_name}' does not exist. Creating it...")
            new_topic = NewTopic(topic_name, num_partitions=1, replication_factor=1)

            admin.create_topics([new_topic])
            print(f"Topic '{topic_name}' created.")
            return topic_name
