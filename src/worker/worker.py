"""Module implements worker object"""
from abc import ABC, abstractmethod
from threading import Event, Thread
from typing import Callable, Dict
import logging
import traceback

from kafka import KafkaConsumer


class WorkerState(ABC):
    """Abstract class defines base elements for worker state"""
    _stop_event: Event

    @property
    def stop_event(self,):
        """Get stop_event included in the state"""
        return self._stop_event

    @abstractmethod
    def reset(self):
        """Reset the current state"""
        raise NotImplementedError()

    def stopping(self):
        """Send stop event"""
        return self._stop_event is not None and self._stop_event.is_set()


class MinimalState(WorkerState):
    """A class that implements simple attributes for worker state"""
    def __init__(self,):
        """Init object's attrinutes"""
        self._stop_event = Event()

    def reset(self):
        """Reset state"""
        pass  # pylint: disable=unnecessary-pass


class ConsumerState(WorkerState):
    """A class that implemets methods and attributes for the kafka consumer worker"""
    def __init__(self, consumer: KafkaConsumer=None):
        """Init object's attributes"""
        self._consumer = consumer
        self._stop_event = Event()
        self._revoked = False

    @property
    def consumer(self,) -> KafkaConsumer:
        """Kafka consumer object"""
        return self._consumer

    @consumer.setter
    def consumer(self, consumer: KafkaConsumer):
        """Update new value for consumer"""
        self._consumer = consumer

    @property
    def revoked(self,):
        """The value indicates whether assigned partitons of the consumer is revoked"""
        return self._revoked

    @revoked.setter
    def revoked(self, revoked: bool):
        """The value indicates whether assigned partitons of the consumer is revoked"""
        self._revoked = revoked

    def reset(self):
        """Reset state"""
        self._revoked = False


class Worker(Thread):
    """A class that implements methods of worker"""
    def __init__(self, name: str, task: Callable, params: Dict, state_type=None):
        """Init worker's attributes"""
        super().__init__(name=name)
        self._state = self._construct_state(state_type=state_type)
        self._task = task
        self._params = params

    def _construct_state(self, state_type: str) -> WorkerState:
        """Init state based on state type input"""
        state_map = {
            "minimal": MinimalState(),
            "consumer": ConsumerState(),
        }
        return state_map[state_type]

    def stop(self):
        """Send stop event to terminate the execution"""
        self._state.stop_event.set()

    def run(self,):
        """Execute task"""
        try:
            self._task(state=self._state, **self._params)
        except Exception:  # pylint: disable=broad-exception-caught
            logging.error("worker <%s> exception: %s", self.name, traceback.format_exc())
