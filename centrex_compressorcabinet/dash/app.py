import datetime
from typing import Optional

import dash_bootstrap_components as dbc
import numpy as np
import plotly.graph_objects as go
from centrex_compressorcabinet import networking
from centrex_compressorcabinet.networking.controller_client import ControlClient

import dash
from dash import MATCH, Input, Output, State, html

from .gui import generate_content


def generate_control_callback(
    app,
    name: str,
    ctrl_name: str,
    ctrl_config: dict,
    status: dict,
    control_client: ControlClient,
):
    ctrl_type = ctrl_config["type"]
    if ctrl_type == "button":
        btn_id = f"{name}-button-{ctrl_name}"

        @app.callback(
            Output(btn_id, "color"),
            Output(btn_id, "children"),
            Input(btn_id, "n_clicks"),
            Input("status-update", "n_intervals"),
            State(btn_id, "children"),
        )
        def do_button(n_clicks: int, n_intervals: int, button_txt: str):

            colors = ctrl_config["colors"]
            values = ctrl_config["values"]
            labels = ctrl_config["labels"]
            functions = ctrl_config["functions"]
            ctx = dash.callback_context

            state = getattr(status[name], ctrl_config["status"])
            if state is None:
                return f"warning, {ctrl_config['status']}?"

            idx = values.index(state)
            if ctx.triggered[0]["prop_id"] == btn_id + ".n_clicks":
                networking.send_command(control_client, name, functions[idx], [], {})

            return colors[idx], labels[idx]

    else:
        return


def generate_control_callbacks(
    app, devices: dict, status: dict, control_client: ControlClient
):
    for name, device_config in devices.items():
        if (ctrls_configs := device_config["GUI"].get("Controls")) is None:
            continue
        else:
            for ctrl_name, ctrl_config in ctrls_configs.items():
                generate_control_callback(
                    app, name, ctrl_name, ctrl_config, status, control_client
                )


def generate_app(
    config: dict,
    data,
    status: dict = {},
    control_client: Optional[ControlClient] = None,
) -> dash.dash.Dash:
    # can select various styles for the web interface
    # app = dash.Dash(external_stylesheets=[dbc.themes.LUX])
    app = dash.Dash(external_stylesheets=[dbc.themes.ZEPHYR])
    # app = dash.Dash(external_stylesheets=[dbc.themes.CERULEAN])

    # app = dash.Dash(external_stylesheets=[dbc.themes.SIMPLEX])
    # app = dash.Dash(external_stylesheets=[dbc.themes.SPACELAB])
    # app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
    # app = dash.Dash(__name__)

    figures, content = generate_content(config, data)
    app.layout = content

    @app.callback(
        Output({"type": "device-figure", "index": MATCH}, "figure"),
        [
            Input({"type": "device-variable-dropdown", "index": MATCH}, "value"),
            Input({"type": "device-figure", "index": MATCH}, "figure"),
            Input({"type": "device-interval", "index": MATCH}, "n_intervals"),
        ],
        [
            State({"type": "device-variable-dropdown", "index": MATCH}, "id"),
        ],
    )
    def update_figure(value, figure, n_intervals, id):
        name = id["index"]

        figure = figures[name]
        figure.data = ()
        x = np.asarray(data[name].timestamp)
        y = np.asarray(getattr(data[name], value))

        figure.add_trace(go.Scatter(x=x, y=y, mode="lines"))

        return figure

    @app.callback(
        Output({"type": "device-accordion-latest", "index": MATCH}, "children"),
        Input({"type": "device-interval", "index": MATCH}, "n_intervals"),
        State({"type": "device-accordion-latest", "index": MATCH}, "id"),
    )
    def update_latest_data(n_intervals, id):
        name = id["index"]
        latest_data = data[name].latest
        latest_data = dict(
            [
                (field, value)
                for field, value in zip(
                    latest_data.__dataclass_fields__, latest_data.as_tuple()
                )
            ]
        )
        table_header = [html.Thead(html.Tr([html.Th("Description"), html.Th("Value")]))]
        rows = []
        for field, value in latest_data.items():
            if field == "timestamp":
                timestamp = datetime.datetime.strftime(value, "%Y-%m-%d %H:%M:%S")
                rows.append(html.Tr([html.Td(field), html.Td(timestamp)]))
            else:
                rows.append(html.Tr([html.Td(field), html.Td(f"{value:.4f}")]))
        table_body = [html.Tbody(rows)]
        return dbc.Table(table_header + table_body, hover=True, striped=True)

    generate_control_callbacks(app, config["Devices"], status, control_client)

    return app
