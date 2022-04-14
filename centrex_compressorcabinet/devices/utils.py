from abc import ABC, abstractmethod
from dataclasses import dataclass
from threading import Event


@dataclass
class DeviceStatus:
    running: bool
    warnings: bool
    errors: bool
    changed: Event

    def json_encodable(self):
        kwargs = dict(
            [
                (field, getattr(self, field))
                if not field == "changed"
                else (field, bool(getattr(self, field)))
                for field in self.__dataclass_fields__.keys()
            ]
        )
        return DeviceStatus(**kwargs)


class DeviceData:
    def as_tuple(self):
        return tuple([getattr(self, field) for field in self.__dataclass_fields__])


class DeviceDriver(ABC):
    @abstractmethod
    def __init__(self, resource_name: str):
        pass

    @abstractmethod
    def get_data(self):
        return
