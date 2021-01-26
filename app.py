'''
Benford validator web app using Dash as a frontend and pandas along with the benford_py library on the backend
Kent 2021
'''

import base64
import datetime
import io

import benford as ben
from dash import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

import db
import layout
import util


# Initialize Dash
external_stylesheets = [dbc.themes.FLATLY]
app = dash.Dash(
    __name__, external_stylesheets=external_stylesheets, title="Benford's Law Validator"
)
application = app.server

# Initialize database for storing historical data
BENDB = db.Db()

# Setup Dash layout
app.layout = layout.mainLayout

# Callback to load data from new file, store dataframe in dash store, and populate dropdown to select column
@app.callback(
    Output("output-data-upload", "children"),
    Output("selectcolumn-dropdown", "options"),
    Output("memory-output", "data"),
    Input("upload-data", "contents"),
    State("upload-data", "filename"),
    State("upload-data", "last_modified"),
)
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children, options, data = load_file(
            list_of_contents, list_of_names, list_of_dates
        )
    else:
        children, data = {}, [{}], {}
    return children, options, data


# Load most flat files and automatically determine delimiter and columns from first line
def load_file(contents, filename, date):
    try:
        content_type, content_string = contents.split(",")
        decoded = base64.b64decode(content_string)
        if "xls" in filename:
            df = pd.read_excel(io.BytesIO(decoded))
        else:
            delim = util.getDelim(decoded)
            df = pd.read_csv(
                io.StringIO(decoded.decode("utf-8")), engine="python", sep=delim
            )
        selections = list(df.columns.values)
        dropdown_selections = [{"label": col, "value": col} for col in selections]
        fileTimestamp = datetime.datetime.fromtimestamp(date).strftime(
            "%m/%d/%Y, %H:%M:%S"
        )
    except Exception as e:
        print(e)
        return (
            html.Div(
                [
                    "There was an error processing this file. Please try a different file."
                ]
            ),
            [{}],
            {},
        )
    return (
        html.Div(
            [
                html.Div(
                    f"Loaded {filename} last modified {fileTimestamp}, please select column of data"
                ),
            ]
        ),
        dropdown_selections,
        {"filename": filename, "dataframe": df.to_dict("records")},
    )


# Callback to load data from specific column in file, validate Benford's Law, 
# display output, save dataset to database, and update historical dataset dropdown
@app.callback(
    Output("output-data-results-new", "children"),
    Output("history-dropdown", "options"),
    Input("selectcolumn-dropdown", "value"),
    Input("memory-output", "data"),
    Input("history-dropdown", "options"),
)
def load_data(value, data, options):
    if value is None:
        raise PreventUpdate
    try:
        df = pd.DataFrame.from_records(data["dataframe"])
        selections = list(df.columns.values)
        index = selections.index(value)
        f1d = ben.first_digits(df.iloc[:, index], digs=1, MAD=True)
        f1d.reset_index(level=0, inplace=True)
        f1dmad = ben.mad(df.iloc[:, index], test=1, decimals=1)
        output = f"Data from {value} exhibits {util.getConformity(f1dmad)} with a mean absolute deviation of {f1dmad}."
        fig = px.bar(
            f1d,
            x="First_1_Dig",
            y="Found",
            barmode="group",
            labels={"First_1_Dig": "First digit", "Found": "Distribution (%)"},
            title="Benford distribution for " + value,
        )
        fig2 = px.line(
            f1d, x="First_1_Dig", y="Expected", color_discrete_map={"Expected": "red"}
        )
        fig.add_trace(fig2.data[0])
        BENDB.insertDataset(f1d, data, value, f1dmad)
        optionslist = BENDB.getDatasetList()
        newoptions = [
            {
                "label": f"File: {result[0]} Column: {result[1]} Upload time: {result[2]}",
                "value": index,
            }
            for index, result in enumerate(optionslist)
        ]
    except Exception as e:
        print(e)
        return (
            html.Div(
                [
                    "There was an error processing the data in this column. Please try a different column."
                ]
            ),
        ), options
    return (
        html.Div(
            [
                dcc.Graph(id="benford-graph", figure=fig),
                html.Div(id="benford-text", children=output),
            ]
        ),
        newoptions,
    )


# Callback to display a historical dataset from database
@app.callback(
    Output("output-data-results-historical", "children"),
    Input("history-dropdown", "value"),
    Input("memory-output", "data"),
)
def load_historical_data(value, data):
    if value is None:
        raise PreventUpdate
    try:
        array, value, f1dmad = BENDB.getDataset(value)
        f1d = pd.read_json(array, typ="series")
        conformity = util.getConformity(f1dmad)
        output = f"Data from {value} exhibits {conformity} with a mean absolute deviation of {f1dmad}."
        digits = f1d.index + 1
        fig = px.bar(
            x=digits,
            y=f1d,
            barmode="group",
            labels={"x": "First digit", "y": "Distribution (%)"},
            title="Benford distribution for " + value,
        )
        fig2 = px.line(
            x=digits, y=util.expected, color_discrete_map={"Expected": "red"}
        )
        fig.add_trace(fig2.data[0])
    except Exception as e:
        print(e)
        return (
            (
                html.Div(
                    [
                        "There was an error processing the data in this dataset. Please try a different dataset."
                    ]
                ),
            ),
        )
    return (
        html.Div(
            [
                dcc.Graph(id="benford-graph", figure=fig),
                html.Div(id="benford-text", children=output),
            ]
        ),
    )


if __name__ == "__main__":
    app.run_server(debug=True)
