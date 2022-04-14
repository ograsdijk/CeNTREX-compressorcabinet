from collections import deque
from dataclasses import dataclass, make_dataclass
from threading import Event
from typing import Tuple, Callable

from centrex_compressorcabinet import devices as devices_drivers
from centrex_compressorcabinet.devices.utils import DeviceStatus


def generate_data_deque_append(device_dataclass) -> Callable:
    """Generate the append function for the dequeu classes holding data for the web
    interface
    """
    fields = list(device_dataclass.__dataclass_fields__.keys())

    def append(deque_dataclass, data):
        for field in fields:
            getattr(deque_dataclass, field).append(getattr(data, field))
        deque_dataclass.latest = data

    return append


def generate_data_deques(devices: dict) -> Tuple[dataclass, dict]:
    """Generate the dictionary holding the deques for the data returned from
    each device
    """
    data = {}
    created_dataclasses = {}
    for name, device in devices.items():
        data_object = getattr(devices_drivers, f"{device['driver']}Data")
        fields = [
            (field_name, deque)
            for field_name in data_object.__dataclass_fields__.keys()
        ]
        created_dataclasses[name] = make_dataclass(
            f"{device['driver']}DataDeque", fields + [("latest", data_object)]
        )
        created_dataclasses[name].append = generate_data_deque_append(data_object)
        data[name] = created_dataclasses[name](
            *([deque(maxlen=device["deque_length"]) for field in fields] + [None])
        )
    return created_dataclasses, data


def generate_status_dataclasses(devices: dict) -> dict:
    """Generate a dictionary holding the status returned from each device"""
    status = {}
    for name, device in devices.items():
        status[name] = DeviceStatus(None, None, None, Event())
    return status
