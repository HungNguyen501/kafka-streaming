"""Module introduces task implementations for the worker"""
import sys
import time
import logging
from typing import Any, List

from src.config.parser import parse_config
from src.worker.worker import ConsumerState
from src.kafka_utils import create_consumer, RebalanceListener, KafkaIO, rewind_offsets


def stream_kafka(state: ConsumerState, topic: str, group_id: str):
    """Stream kafka data to database"""
    config = parse_config().kafka
    consumer = create_consumer(
        topic=topic,
        group_id=group_id,
        config=config,
    )
    state.consumer = consumer
    logging.info("created kafka consumer on %s, group: %s", config.kafka_brokers, group_id)
    try:
        consumer.subscribe(topics=[topic,], listener=RebalanceListener(state=state))
        logging.info("subscribed for topic %s", topic)
        while not state.stopping():
            state.reset()
            stream = KafkaIO(state=state, config=config.consumer)
            data = []
            for i in stream:
                data.append(i)
            if insert_to_db(data=data):
                consumer.commit()
            else:
                rewind_offsets(consumer=consumer)
    finally:
        consumer.close()
        logging.info("closed kafka consumer on topic %s", topic)


def insert_to_db(data: List[Any]) -> bool:
    """Simulate ETL pipeline"""
    if data:
        logging.info("inserted %d bytes to db", sys.getsizeof(data))
    return True


def greeting(message: str, **kwargs):  # pylint: disable=unused-argument
    """Show the greeting message to console"""
    for i in range(5):
        time.sleep(i)
        logging.info(message)
