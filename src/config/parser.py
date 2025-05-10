"""Module implements config parser"""
import yaml

from src.config.model import AppConfig, DbConfig, KafkaConfig, TaskConfig, KafkaConsumerConfig


def parse_config(file_path: str = "./config/app-config.yaml") -> AppConfig:
    """Parse config file to AppConfig object"""
    with open(file=file_path, mode="r", encoding="utf-8") as stream:
        data = yaml.safe_load(stream)
        kafka_cfg = data["kafka"]
        tasks = []
        db = DbConfig(**data["database"])
        kafka = KafkaConfig(
            kafka_brokers=kafka_cfg["kafka_brokers"],
            sasl_mechanism=kafka_cfg["sasl_mechanism"],
            sasl_password=kafka_cfg["sasl_password"],
            sasl_protocol=kafka_cfg["sasl_protocol"],
            sasl_user=kafka_cfg["sasl_user"],
            consumer=KafkaConsumerConfig(**kafka_cfg["consumer"]),
        )
        for name, info in data["tasks"].items():
            info["name"] = name
            tasks.append(TaskConfig(**info))
        return AppConfig(
            kafka=kafka,
            db=db,
            tasks=tasks,
            task_validation_interval=data["task_validation_interval"],
        )
