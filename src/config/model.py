"""Module implements models for multi kinds of application configs"""
from dataclasses import dataclass
from typing import List


@dataclass
class KafkaConsumerConfig:
    """Kafka consumer configurations"""
    max_block_size: int
    max_consume_time: int
    max_data_size: int
    poll_max_records: int
    poll_timeout_ms: int


@dataclass
class KafkaConfig:
    """Kafka configurations"""
    kafka_brokers: str
    sasl_protocol: str
    sasl_mechanism: str
    sasl_user: str
    sasl_password: str
    consumer: KafkaConsumerConfig


@dataclass
class DbConfig:
    """"Database configurations"""
    protocol: str
    url: str
    replica_url: str
    name: str
    username: str
    password: str
    port: int
    max_db_conns: int
    max_conn_lifetime: int
    max_conn_idle_time: int


@dataclass
class TaskConfig:
    """"Task configurations"""
    name: str
    state_type: str
    function: str
    arguments: dict


@dataclass
class AppConfig:
    """Application configurations"""
    kafka: KafkaConfig
    db: DbConfig
    worker_healthcheck_interval: int
    tasks: List[TaskConfig]
