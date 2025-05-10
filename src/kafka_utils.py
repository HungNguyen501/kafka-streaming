"""Module implements kafka setups"""
import time
import logging

from kafka import KafkaConsumer, ConsumerRebalanceListener

from src.worker.worker import ConsumerState
from src.config.model import KafkaConfig, KafkaConsumerConfig


def create_consumer(
    topic: str,
    group_id: str,
    config: KafkaConfig,
    auto_commit: bool=False,
    value_deserializer=None,
    key_deserializer=None,
):
    """Create kafka consumer"""
    return KafkaConsumer(
        topic,
        bootstrap_servers=config.kafka_brokers.split(","),
        # security_protocol=config.sasl_protocol,
        # sasl_mechanism=config.sasl_mechanism,
        # sasl_plain_username=config.sasl_user,
        # sasl_plain_password=config.sasl_password,
        group_id=group_id,
        value_deserializer=value_deserializer,
        key_deserializer=key_deserializer,
        auto_offset_reset = 'earliest',
        enable_auto_commit=auto_commit,
    )


def rewind_offsets(consumer: KafkaConsumer):
    """Seek to committed offsets of partitions of the consumer"""
    for tp in consumer.assignment():
        committed_offset = consumer.committed(tp)
        consumer.seek(tp, committed_offset)


class KafkaIO:
    """
        A class that customizes data consumption of the kafka consumer.
        The class enforces limits on both the duration and volume of consumption,
        also provides a generator to iterate over the incoming data.
    """
    def __init__(self, state: ConsumerState, config: KafkaConsumerConfig,):
        """Init object's attributes"""
        self._state = state
        self._consumed_block_size = 0
        self._consumed_data_size = 0
        self._consume_start = time.time()
        self._poll_timeout_ms = config.poll_timeout_ms
        self._poll_max_records = config.poll_max_records
        self._max_block_size = config.max_block_size
        self._max_data_size = config.max_data_size
        self._max_consume_time = config.max_consume_time

    def __iter__(self):
        """Create iterator"""
        return self

    def __next__(self):
        """Return batch of consumed data when next element is called"""
        if (time.time() - self._consume_start) > self._max_consume_time \
            or (self._max_data_size and self._consumed_data_size >= self._max_data_size) \
            or (self._max_block_size and self._consumed_block_size >= self._max_block_size):
            logging.warning("stop iteration because data consumption limit reached")
            raise StopIteration

        if self._state.revoked:
            logging.warning("stop iteration because partition revoked")
            raise StopIteration

        if self._state.stopping():
            logging.warning("stop iteration because worker stopping")
            raise StopIteration

        poll_data = self._state.consumer.poll(timeout_ms=self._poll_timeout_ms, max_records=self._poll_max_records)
        if not poll_data:
            logging.warning("stop iteration because poll() return empty")
            raise StopIteration

        data, count, size = self._squash_poll_data(poll_data)
        self._consumed_block_size += count
        self._consumed_data_size += size
        return data

    def _squash_poll_data(self, poll_data):
        """Start polling data"""
        values = []
        total_messages = 0
        total_bytes = 0
        for _, messages in poll_data.items():
            for m in messages:
                values.append(m.value)
                total_messages += 1
                total_bytes += len(m.value)
        return b''.join(values), total_messages, total_bytes


class RebalanceListener(ConsumerRebalanceListener):
    """
        A class that implements ConsumerRebalanceListener interface to trigger custom actions
        when the set of partitions assigned to the consumer changes.
    """
    def __init__(self, state: ConsumerState):
        """Init object"""
        super().__init__()
        self._state = state

    def on_partitions_assigned(self, assigned):
        """Log event when the consumer is assgined to a partition"""
        if assigned:
            logging.info("partitions assigned: %s", assigned)

    def on_partitions_revoked(self, revoked):
        """
            Log the event that occurs before a rebalance operation starts and 
            after the consumer stops fetching data
        """
        if revoked:
            logging.info("partitions revoked: %s", revoked)
            self._state.revoked = True
