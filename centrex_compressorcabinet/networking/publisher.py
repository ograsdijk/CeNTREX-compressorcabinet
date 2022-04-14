import json
import time
from queue import Queue
from threading import Event, Thread

import zmq

from .json_utils import EnhancedJSONEncoder


class Publisher(Thread):
    def __init__(self, port: int):
        super(Publisher, self).__init__()

        # deamon = True ensures this thread terminates when the main threads are
        # terminated
        self.daemon = True

        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.bind(f"tcp://*:{port}")

        self.queue = Queue()

        self.active = Event()

    def encode(self, topic: str, message: str) -> str:
        """
        Function encodes the message from the publisher via json serialization

        Args:
            topic (str): topic of message
            message (str): message

        Returns:
            str: topic and message with json encoding
        """
        return topic + ":" + " " + json.dumps(message, cls=EnhancedJSONEncoder)

    def run(self):
        while self.active.is_set():
            while not self.queue.empty():
                topic, driver, message = self.queue.get()
                # print(topic, driver)
                self.socket.send_string(self.encode(topic, [driver, message]))
            time.sleep(1e-5)
