import time
from queue import Queue
from threading import Event, Thread

from centrex_compressorcabinet import devices


class MainRunner(Thread):
    def __init__(self, devices: dict, publisher):
        super(MainRunner, self).__init__()

        # deamon = True ensures this thread terminates when the main threads are
        # terminated
        self.daemon = True

        self.devices = dict(
            [
                (name, DeviceRunner(device_config["driver"], name, device_config))
                for name, device_config in devices.items()
            ]
        )
        self.publisher = publisher

        self.command_queue = Queue()
        # potentially unsafe, not sure how else to handle the ID lookup
        self.command_return = {}

        self.active = Event()

    def run(self):
        for name, device in self.devices.items():
            device.active.set()
            device.start()
        while self.active.is_set():
            for name, device in self.devices.items():
                while not device.data_queue.empty():
                    dat = device.data_queue.get()
                    self.publisher.queue.put((name, device.driver, dat))
                while not device.status_queue.empty():
                    status = device.status_queue.get()
                    self.publisher.queue.put((f"status-{name}", device.driver, status))
                while not device.command_return.empty():
                    id, ret = device.command_return.get()
                    self.command_return[id] = ret

            while not self.command_queue.empty():
                id, name, command, args, kwargs = self.command_queue.get()
                self.devices[name].command_queue.put((id, command, args, kwargs))
                time.sleep(1e-6)

            time.sleep(1e-6)
        for name, device in self.devices.items():
            self.device.active.clear()


class DeviceRunner(Thread):
    def __init__(self, driver: str, name: str, config: dict):
        super(DeviceRunner, self).__init__()

        # deamon = True ensures this thread terminates when the main threads are
        # terminated
        self.daemon = True

        self.name = name

        self.status_queue = Queue()
        self.data_queue = Queue()
        self.command_queue = Queue()
        self.command_return = Queue()

        self.dt = config["dt"]
        self.driver = driver
        self.device = getattr(devices, driver)(**config["construction parameters"])

        self.active = Event()

    def run(self):
        t = time.time()
        while self.active.is_set():
            # run get_data function on a dt interval
            if time.time() - t >= self.dt:
                t = time.time()
                dat = self.device.get_data()
                self.data_queue.put(dat)
            if self.device.status.changed.is_set():
                self.status_queue.put(self.device.status.json_encodable())
                self.device.status.changed.clear()
            # check for commands
            while not self.command_queue.empty():
                id, command, args, kwargs = self.command_queue.get()
                ret = getattr(self.device, command)(*args, **kwargs)
                self.command_return.put((id, ret))
            time.sleep(1e-6)
