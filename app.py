import base64
import io

import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from dash import dcc

from dash import html
from dash import dash_table

import pandas as pd

app = dash.Dash(__name__)

server = app.server

app.layout = html.Div([
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        multiple=False
    ),
    html.Div(id='output-data-upload'),
])

def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    # Create input table with editable=True property
    input_table = dash_table.DataTable(
        id='input-table',
        columns=[{'name': i, 'id': i} for i in df.columns],
        data=df.to_dict('records'),
        editable=True,
        page_size=15,
    )

    # Create mean table with initial values
    mean_df = df.select_dtypes(include='number').mean().reset_index()
    mean_df.columns = ['Column Name', 'Mean Value']
    mean_table = dash_table.DataTable(
        id='mean-table',
        columns=[{'name': i, 'id': i} for i in mean_df.columns],
        data=mean_df.to_dict('records'),
    )

    return html.Div([
        html.H5(filename),
        input_table,
        html.Hr(),
        html.H5('Mean Table'),
        mean_table
    ])

@app.callback(
    dash.dependencies.Output('output-data-upload', 'children'),
    [dash.dependencies.Input('upload-data', 'contents')],
    [dash.dependencies.State('upload-data', 'filename')]
)
def update_output(contents, filename):
    if contents is not None:
        children = [
            parse_contents(contents, filename)
        ]
        return children

if __name__ == '__main__':
    app.run_server(debug=False)
