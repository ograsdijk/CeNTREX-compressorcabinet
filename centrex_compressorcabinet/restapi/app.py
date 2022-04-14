import contextlib
import time
from typing import Optional
from threading import Thread
import uvicorn
from pydantic import BaseModel
from centrex_wavelengthmeter import devices

from fastapi import FastAPI, HTTPException, encoders


class FastAPIServer(uvicorn.Server):
    def install_signal_handlers(self):
        pass

    @contextlib.contextmanager
    def run_in_thread(self):
        thread = Thread(target=self.run)
        thread.start()
        try:
            while not self.started:
                time.sleep(1e-3)
            yield
        finally:
            self.should_exit = True
            thread.join()


def generate_fastapi_app(devices_dict, data):
    app = FastAPI()

    @app.get("/")
    def get_all_devices():
        return list(devices_dict.keys())

    @app.get("/{device}")
    def get_device_return_types(device):
        d = getattr(devices, f"{devices_dict[device]}Data")

        fields = d.__dataclass_fields__
        return_val = dict(
            [
                (name, field.type.__name__)
                if name != "timestamp"
                else (name, "isoformat")
                for name, field in fields.items()
            ]
        )
        print(return_val)
        return encoders.jsonable_encoder(return_val)

    @app.get("/{device}/get_data")
    def get_data(device):
        if device not in data:
            raise HTTPException(status_code=404, detail=f"{device=} not found")
        return encoders.jsonable_encoder(data[device].get_current())

    return app
