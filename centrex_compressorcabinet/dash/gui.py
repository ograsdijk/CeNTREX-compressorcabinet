import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from centrex_compressorcabinet import devices
from plotly.graph_objs._figure import Figure

from dash import dcc, html


def generate_device_figure(name: str, device_config: dict):
    """Generate a plotly figure for a device"""
    layout = go.Layout(margin=go.layout.Margin(l=0, r=0, b=0, t=0), uirevision=True)
    figure = Figure(layout=layout)
    data_object = getattr(devices, f"{device_config['driver']}Data")
    fields = [
        field_name
        for field_name in data_object.__dataclass_fields__.keys()
        if not field_name == "timestamp"
    ]

    id = {"type": "device-variable-dropdown", "index": name}
    figure_dropdown = dcc.Dropdown(fields, fields[0], id=id)

    id = {"type": "device-figure", "index": name}
    return figure, dcc.Graph(figure=figure, id=id), figure_dropdown


def generate_device_controls(name: str, device_config: dict):
    """Generate the device controls for a device, as specified in device_config"""
    ctrls_config = device_config["GUI"].get("Controls")
    if ctrls_config is None:
        return

    ctrls = []
    for ctrl_name, ctrl_config in ctrls_config.items():
        if ctrl_config["type"] == "button":
            # id = {"type": f"device-button-{ctrl_name}", "index": name}
            id = f"{name}-button-{ctrl_name}"
            labels = ctrl_config["labels"]
            colors = ctrl_config["colors"]
            ctrl = dbc.Button(labels[0], id=id, color=colors[0])
            ctrls.append(ctrl)
    return ctrls


def generate_accordion_latest_values(name: str):
    """Generate the accordion holding the latest data read out from a device"""
    id = {"type": "device-accordion-latest", "index": name}
    accordion = dbc.Accordion(
        dbc.AccordionItem([], title="Latest data", id=id), start_collapsed=True
    )
    return accordion


def generate_device_subpage(name: str, device_config: dict):
    """Generate the subpage for a device with name `name` and a configuration specified
    in device_config
    """
    # controls
    ctrls = generate_device_controls(name, device_config)
    controls = [dbc.Row(ctrls)]

    # figure
    figure, graph, figure_dropdown = generate_device_figure(name, device_config)

    device_graph_control = dbc.Row(
        dbc.Accordion(
            dbc.AccordionItem(children=[graph, figure_dropdown], title="Graph"),
            start_collapsed=True,
        )
    )
    id = {"type": "device-interval", "index": name}
    dt = device_config.get("dt", device_config["dt"])
    figure_content = [
        device_graph_control,
        dcc.Interval(interval=dt * 1e3, id=id),
    ]

    # latest data table
    latest_data = generate_accordion_latest_values(name)
    # generate subpage

    # generate the 'card' for each device
    id = {"type": "device-cardheader", "index": name}
    device_subpage = dbc.Card(
        [
            dbc.CardHeader(children=html.H5(name, className="card-title"), id=id),
            dbc.CardBody(controls + figure_content + [latest_data]),
        ],
        # class_name="card border-secondary mb-3",
    )

    return figure, device_subpage


def generate_content(config: dict, data):
    """Generat the layout for the page and all devices"""
    figures = {}

    layout = {}

    # iterate through devices and determine the layout from the config dictionary
    max_rows = 0
    max_columns = 0
    for name, device_config in config["Devices"].items():
        gui_config = device_config["GUI"]
        column, row = gui_config["column"], gui_config["row"]
        max_rows = max(max_rows, row + 1)
        max_columns = max(max_columns, column + 1)
        layout[(column, row)] = name

    # interate through the layout and create the device subpages
    rows = []
    for row in range(max_rows):
        columns = []
        for col in range(max_columns):
            if (name := layout.get((col, row))) is None:
                continue

            figure, device_subpage = generate_device_subpage(
                name, config["Devices"][name]
            )
            columns.append(device_subpage)
            figures[name] = figure
        rows.append(dbc.CardGroup(columns))

    content = html.Div(
        [dbc.Row(row) for row in rows]
        + [dcc.Interval(interval=config["GUI"]["dt"] * 1e3, id="status-update")]
    )

    return figures, content
