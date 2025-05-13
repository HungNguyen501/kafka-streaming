"""Module implements the coordinator for worker group"""
from typing import Dict
import time
import logging

from src.config.parser import AppConfig
from src.worker.worker import Worker
import src.task


class Coordinator:
    """A class that coordinates a group of workers"""
    def __init__(self,config: AppConfig):
        """Init object's attributes"""
        self.workers: Dict[str, Worker] = {}
        self.config = config
        self.validation_time = 0

    def start(self,):
        """Start to assign tasks to workers and do clean up dead workers by interval"""
        for task in self.config.tasks:
            worker = Worker(
                name=task.name,
                task=getattr(src.task, task.function),
                state_type=task.state_type,
                params=task.arguments,
            )
            self.workers[task.name] = worker
            worker.start()

        while True:
            time_now = time.time()
            if time_now - self.validation_time > self.config.worker_healthcheck_interval:
                self.validation_time = time_now
                self.cleanup_dead_workers()
                if not self.workers:
                    break

    def cleanup_dead_workers(self,):
        """Delete workers that are no longer running"""
        for name in list(self.workers.keys()):
            if not self.workers[name].is_alive():
                del self.workers[name]
                logging.debug("removed dead worker %s", name)

    def stop_all_workers(self,):
        """Stop all workers"""
        for w in self.workers.values():
            w.stop()
        for w in self.workers.values():
            w.join()
            assert not w.is_alive(), f"worker {w.name} does not terminate"

    def __enter__(self,):
        """Enter context manager"""
        return self

    def __exit__(self,*_):
        """Exit context manager"""
        self.stop_all_workers()
