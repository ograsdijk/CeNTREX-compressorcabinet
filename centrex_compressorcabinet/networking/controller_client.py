import logging
import time
import uuid
from queue import Queue
from threading import Event, Thread

import zmq


class ControlClient(Thread):
    def __init__(self, port: int):
        super(ControlClient, self).__init__()
        self.daemon = True
        self.command_queue = Queue()
        self.command_return = {}
        self.command_return_popque = Queue()
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.port = port
        self.timeout = 5000

        self.active = Event()

    def execute_command(self, device, command, args, kwargs, id=None):
        self.socket.send_json([device, command, args, kwargs])

        if (self.socket.poll(self.timeout) & zmq.POLLIN) != 0:
            status, retval = self.socket.recv_json()
            if status == "OK":
                return retval
            else:
                logging.warning(
                    f"{device} networking warning in "
                    + f"ExecuteNetworkCommand : error for {command} -> {retval}"
                )
                return "Error"

    def run(self):
        self.socket.connect(f"tcp://localhost:{self.port}")
        while self.active.is_set():
            while not self.command_queue.empty():
                id, device, command, args, kwargs = self.command_queue.get()
                ret = self.execute_command(device, command, args, kwargs)
                self.command_return[id] = ret

            while not self.command_return_popque.empty():
                self.command_return.pop(self.command_return_popque.get())

            time.sleep(1e-6)


def send_command(
    control_client: ControlClient, device, command, args, kwargs, wait_return=False
):
    id = uuid.uuid1().int >> 64
    control_client.command_queue.put([id, device, command, args, kwargs])
    if wait_return:
        while True:
            if id in control_client.command_return:
                ret = control_client.command_return.pop(id)
                return ret
            time.sleep(1e-6)
    else:
        control_client.command_return_popque.put(id)
    return
