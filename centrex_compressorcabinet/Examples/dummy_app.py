from pathlib import Path

# import plotly.express as px
import yaml
from centrex_compressorcabinet.dash.app import generate_app
from centrex_compressorcabinet.networking import (
    Broker,
    Publisher,
    PublisherClient,
    Worker,
    ControlClient,
)
from centrex_compressorcabinet.runner import (
    MainRunner,
    generate_data_deques,
    generate_status_dataclasses,
)

with Path("./config.yml").open() as f:
    config = yaml.safe_load(f)

# global variables to keep data synchronized
# class with deques to hold the data
_, data = generate_data_deques(config["Devices"])
# class to hold the status for each device
status = generate_status_dataclasses(config["Devices"])

# start the control client that handles sending commands to the runner controlling
# communication with the devices
control_client = ControlClient(config["Networking"]["control port"])

# generate the app (with layout and callbacks)
app = generate_app(config, data, status, control_client)

if __name__ == "__main__":
    # start the data publisher
    publisher = Publisher(config["Networking"]["publisher port"])
    publisher.active.set()
    publisher.start()

    # start the threads running communication with each device
    devices_runner = MainRunner(config["Devices"], publisher)
    devices_runner.active.set()
    devices_runner.start()

    # starting the publisher client that recieved data from the publisher and puts it
    # into the data and status storage
    publisher_client = PublisherClient(
        config["Networking"]["publisher port"], data, status
    )
    publisher_client.active.set()
    publisher_client.start()

    # start the network broker and workers to handle commands to devices
    broker = Broker(config["Networking"]["control port"])

    broker.start()

    workers = []
    for _ in range(10):
        workers.append(Worker(broker.backend_port, devices_runner))
        workers[_].active.set()
        workers[_].start()

    # start the client
    control_client.active.set()
    control_client.start()

    import logging

    # start the web interface
    log = logging.getLogger("compressor_cabinet")
    log.setLevel(logging.ERROR)
    app.run_server(debug=False, host="0.0.0.0")
