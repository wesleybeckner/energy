# -*- coding: utf-8 -*-
import dash
import json
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
from plotly.subplots import make_subplots
import plotly.graph_objects as go

import pandas as pd
import numpy as np
import datetime

data = pd.read_excel('data/energy.xlsx', sheet_name='Data for Dashboard', header=0)
data = data.set_index(['Item', 'Units', 'Plant'])

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)
server = app.server

def make_time_plot(clickData=None):
    if clickData != None:
        print(clickData)
        line = clickData['points'][0]['label']
    else:
        line = 'PC'
    GJ = data.reorder_levels([2,1,0]).loc[line, 'GJ']#.droplevel(1)
    GJ = GJ.T[['Electricity', 'Nat. Gas', 'Steam usage']].T
    mtmt = data.reorder_levels([2,1,0]).loc[line, 'mt/mt']
    mtmt.T.loc[mtmt.T["CO2/production"] == 0] = np.nan

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    for index in GJ.index:
        fig.add_trace(
        go.Scatter(
        name=index,
        y=GJ.loc[index],
        x=GJ.columns,
        ),
        secondary_y=False
    )

    for index in mtmt.index:
        fig.add_trace(
        go.Scatter(
        name=index,
        y=mtmt.loc[index],
        x=mtmt.columns,
        ),
        secondary_y=True
    )

    fig.update_yaxes(title_text="<b>Energy Usage</b> (GJ)", secondary_y=False)
    fig.update_yaxes(title_text="<b>CO2/Production</b> (MT/MT)", secondary_y=True)

    fig.update_layout(dict(
        barmode="stack",
    ),
    )
    return fig


def make_bar_plot():
    # create usage df
    df = data.mean(axis=1).reorder_levels([2,1,0])
    df = pd.DataFrame(df).unstack()
    df = df.reorder_levels([1,0]).loc['GJ'][0].dropna(axis=1)
    df['Totals'] = df.sum(axis=1)
    df = df.sort_values(by='Totals')

    # create CO2/MT df
    df2 = pd.DataFrame(data.mean(axis=1)).loc['CO2/production']
    df2 = df2.loc['mt/mt']
    df2.columns = ['CO2/production']
    df2 = df2.reindex(df.index)
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    for col in df.columns[:-1]:
        fig.add_trace(
        go.Bar(
        name=col,
        y=df[col],
        x=df.index,
        ),
        secondary_y=False
    )

    for col in df2.columns:
        fig.add_trace(
        go.Scatter(
        name=col,
        y=df2[col],
        x=df2.index,
        ),
        secondary_y=True
    )

    fig.update_yaxes(title_text="<b>Energy Usage</b> (GJ)", secondary_y=False)
    fig.update_yaxes(title_text="<b>CO2/Production</b> (MT/MT)",
        secondary_y=True)

    fig.update_layout(dict(
        barmode="stack",
    ),
    )
    return fig

# Describe the layout/ UI of the app
app.layout = html.Div([
    dcc.Graph(id='bar_plot',
              figure=make_bar_plot()
              ),
    dcc.Graph(id='time_plot',
              figure=make_time_plot()
              ),
              ],
              className="pretty_container"
              )

app.config.suppress_callback_exceptions = False

# Update page
@app.callback(
    Output('time_plot', 'figure'),
    [Input('bar_plot', 'clickData')]
)
def display_time_plot(barClickData):
    return make_time_plot(barClickData)

if __name__ == "__main__":
    app.run_server(debug=True)
