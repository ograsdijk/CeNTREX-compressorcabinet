import datetime
from dataclasses import dataclass
from threading import Event

import numpy as np

from .utils import DeviceDriver, DeviceData, DeviceStatus


@dataclass
class CPA1110Data(DeviceData):
    timestamp: datetime
    coolant_input_temperature: float
    coolant_output_temperature: float
    oil_temperature: float
    helium_pressure: float
    low_pressure: float
    low_pressure_average: float
    high_pressure: float
    high_pressure_average: float
    delta_pressure_average: float
    motor_current: float


class CPA1110(DeviceDriver):
    def __init__(self, resource_name: str):
        self.resource_name = resource_name
        self.status = DeviceStatus(False, False, False, Event())
        self.status.changed.set()

    def get_data(self) -> CPA1110Data:
        return CPA1110Data(
            datetime.datetime.now(),
            np.random.randn(),
            np.random.randn(),
            np.random.randn(),
            np.random.randn(),
            np.random.randn(),
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
