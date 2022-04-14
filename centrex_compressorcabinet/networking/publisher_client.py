import datetime
import json
import time
from threading import Event, Thread

import zmq
from centrex_compressorcabinet import devices


class PublisherClient(Thread):
    def __init__(self, port: int, data: dict, status: dict):
        super(PublisherClient, self).__init__()

        self.daemon = True
        self.data = data
        self.status = status

        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.port = port

        self.active = Event()

    def handle_status(self, topic: str, data: str):
        """
        Handle the status return from a Publisher
        """
        name = topic.lstrip("status-")
        data = json.loads(data)
        # driver = data[0]
        data = data[1]
        for field, value in data.items():
            setattr(self.status[name], field, value)

    def handle_data(self, topic: str, data: str):
        """
        Handle the data return from a Publisher
        """
        name = topic
        data = json.loads(data)
        data[1]["timestamp"] = datetime.datetime.fromisoformat(data[1]["timestamp"])
        driver = data[0]
        data = data[1]
        self.data[name].append(getattr(devices, f"{driver}Data")(**data))

    def handle_message(self, message: str):
        """
        Handle a message from a Publisher
        """
        topic, dat = message.split(":", 1)
        if "status" in topic:
            self.handle_status(topic, dat)
        else:
            self.handle_data(topic, dat)

    def run(self):
        self.socket.connect(f"tcp://localhost:{self.port}")
        self.socket.setsockopt_string(zmq.SUBSCRIBE, "")
        while self.active.is_set():
            self.handle_message(self.socket.recv_string())
            time.sleep(1e-6)
