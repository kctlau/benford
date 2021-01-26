'''
Layout file for Benford's law validator webapp
'''

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

# Layout for new data card
newFile = dbc.Card(
    [
        dbc.FormGroup(
            [
                dbc.Label("Load New File"),
                dcc.Upload(
                    id="upload-data",
                    children=html.Div(["Drag and Drop or ", html.A("Select File")]),
                    style={
                        "width": "100%",
                        "height": "40px",
                        "lineHeight": "40px",
                        "borderWidth": "1px",
                        "borderStyle": "dashed",
                        "borderRadius": "5px",
                        "textAlign": "center",
                        # "margin": "10px",
                    },
                    multiple=False,
                ),
                html.Div(id="output-data-upload"),
                dcc.Dropdown(
                    id="selectcolumn-dropdown",
                    placeholder="Select column",
                ),
            ],
        ),
    ],
    body=True,
)

# Layout for historical data card
oldData = dbc.Card(
    [
        dbc.FormGroup(
            [
                dbc.Label("Or Select Historical Dataset"),
                dcc.Dropdown(
                    id="history-dropdown",
                    options=[],
                    placeholder="Select historical dataset",
                ),
            ],
        ),
    ],
    body=True,
)

# Layout for new data tab
new_data_tab = (
    newFile,
    html.Div(id="output-data-results-new"),
)

# Layout for historical data tab
historical_data_tab = (
    oldData,
    html.Div(id="output-data-results-historical"),
)

# Main layout
mainLayout = dbc.Container(
    children=[
        html.H1(children="Benford's Law Validator"),
        html.Hr(),
        dbc.Tabs(
            [
                dbc.Tab(new_data_tab, label="New Data"),
                dbc.Tab(historical_data_tab, label="Historical Data"),
            ]
        ),
        dcc.Store(id="memory-output"),
    ],
    fluid=True,
    className="p-5",
)