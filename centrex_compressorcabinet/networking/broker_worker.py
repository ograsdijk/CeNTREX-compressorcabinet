import time
import uuid
from threading import Event, Thread

import zmq
from centrex_wavelengthmeter.runner import MainRunner


class Worker(Thread):
    def __init__(self, port: int, main_runner: MainRunner):
        super(Worker, self).__init__()
        self.active = Event()
        self.daemon = True
        self.port = port

        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.main_runner = main_runner

    def run(self):
        self.socket.connect(f"tcp://localhost:{self.port}")
        while self.active.is_set():
            name, command, args, kwargs = self.socket.recv_json()
            id = uuid.uuid1().int >> 64
            self.main_runner.command_queue.put([id, name, command, args, kwargs])
            while True:
                if id in self.main_runner.command_return:
                    ret = self.main_runner.command_return.pop(id)
                    self.socket.send_json(["OK", ret])
                    break
                time.sleep(1e-6)


class Broker(Thread):
    def __init__(self, port: int):
        super(Broker, self).__init__()
        self.daemon = True

        self.context = zmq.Context()

        self.frontend = self.context.socket(zmq.XREP)
        self.backend = self.context.socket(zmq.XREQ)

        self.frontend.bind(f"tcp://*:{port}")

        self.backend_port = self.backend.bind_to_random_port("tcp://127.0.0.1")

    def run(self):
        try:
            zmq.device(zmq.QUEUE, self.frontend, self.backend)
        except zmq.error.ZMQError:
            pass
