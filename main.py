"""Module runs main program"""
import logging
import logging.config

from src.config.parser import parse_config
from src.worker.coordinator import Coordinator

logging.config.fileConfig(fname="config/logging.cfg")
logging.getLogger(__name__)


if __name__ == "__main__":
    with Coordinator(config=parse_config()) as coordinator:
        coordinator.start()
