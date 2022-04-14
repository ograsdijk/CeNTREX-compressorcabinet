import datetime
from dataclasses import dataclass
from threading import Event

import numpy as np

from .utils import DeviceDriver, DeviceData, DeviceStatus


@dataclass
class nXDSData(DeviceData):
    timestamp: datetime
    voltage: float
    current: float
    power: float
    pump_temperature: float
    pump_control_temperature: float


class nXDS(DeviceDriver):
    def __init__(self, resource_name: str):
        self.resource_name = resource_name
        self.status = DeviceStatus(False, False, False, Event())
        self.status.changed.set()

    def get_data(self) -> nXDSData:
        return nXDSData(
            datetime.datetime.now(),
            np.random.randn(),
            np.random.randn(),
            np.random.randn(),
            np.random.randn(),
            np.random.randn(),
        )

    def start(self):
        if not self.status.running:
            self.status.running = True
            self.status.changed.set()

    def stop(self):
        if self.status.running:
            self.status.running = False
            self.status.changed.set()
