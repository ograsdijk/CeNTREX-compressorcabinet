from centrex_wavelengthmeter import restapi
from centrex_wavelengthmeter import networking
from centrex_wavelengthmeter import dash
from pathlib import Path
import yaml

with Path("./config.yml").open() as f:
    config = yaml.safe_load(f)

data = dash.gui.initialize_data_classes(
    config["Data"]["deque length"], config["FiberPorts"]
)

data = {"CeNTREX Wavelengthmeter": data}

devices = dict([(name, device["driver"]) for name, device in config["Devices"].items()])
client = networking.PublisherClient(config["Networking"]["publisher port"], data)
client.active.set()
client.start()

app = restapi.generate_fastapi_app(devices, data)
