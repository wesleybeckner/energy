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
data.columns = pd.to_datetime(data.columns)
axis_options = data.index.get_level_values(0).unique()

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)
server = app.server

# def make_year_plot():
#     GJ = data.loc[data.index.get_level_values(0).isin(['Electricity', 'Nat. Gas', 'Steam usage'])]\
#         .groupby('Item').sum().T.resample('Y').sum().T
#
#     mtmt = data.loc[data.index.get_level_values(0).isin(['CO2/production'])]\
#         .groupby('Item').sum().T.resample('Y').sum().T
#
#     GJmt = data.loc[data.index.get_level_values(0).isin(['Energy Intensity'])]\
#         .groupby('Item').sum().T.resample('Y').sum().T
#
#     mt = data.loc[data.index.get_level_values(0).isin(['Production', 'CO2'])]\
#         .groupby('Item').sum().T.resample('Y').sum().T
#
#     fig = make_subplots(specs=[[{"secondary_y": True}]])
#     df = mt
#     for index in df.index:
#         fig.add_trace(
#         go.Bar(
#         name=index,
#         y=df.loc[index],
#         x=df.columns,
#         ),
#         secondary_y=False
#     )
#     fig.update_layout(dict(
#     barmode="stack",
#     ),
#     )
#     return fig

def make_time_plot(clickData=None, selectedData=None, dropdown=None):
    if dropdown != None:
        items = dropdown
    else:
        items = ['Electricity', 'Nat. Gas', 'Steam usage', 'CO2/production']
    if selectedData != None:
        line = pd.Series(pd.DataFrame.from_dict(selectedData['points'])['x'].unique())
    elif clickData != None:
        line = clickData['points'][0]['label']
    else:
        line = data.index.get_level_values(2).unique()

    if type(line) == str:
        line = pd.Series(line)

    df = data.loc[(data.index.get_level_values(2).isin(line)) & # grab the right lines
             (data.index.get_level_values(0).isin(items))]

    units = df.index.get_level_values(1).unique() # detect number of different unit types; compute axes

    fig = go.Figure()
    if len(units) == 1:
        titles = ["{}".format(df.index.get_level_values(1).unique()[0])]
        if '/' not in units: # sum Item values if no '/' otherwise take weight average
            for index in df.index.get_level_values(0).unique():
                fig.add_trace(
                go.Scatter(
                name=index,
                y=df.loc[index].sum(),
                x=df.columns,
                ),
            )
        else:
            for index in df.index.get_level_values(0).unique():
                fig.add_trace(
                go.Scatter(
                name=index,
                y=df.loc[index].mean(),
                x=df.columns,
                ),
            )
    else:

        titles = []
        for index2, unit in enumerate(units):
            df2 = df.loc[(df.index.get_level_values(1) == unit)]
            titles.append("{}".format(df2.index.get_level_values(1).unique()[0]))
            if '/' not in unit: # sum Item values if no '/' otherwise take weight average
                for index in df2.index.get_level_values(0).unique():
                    fig.add_trace(
                    go.Scatter(
                    name="{} ({})".format(index,unit),
                    y=df2.loc[index].sum(),
                    x=df2.columns,
                    yaxis="y{}".format(index2+1)
                    ),
                )
            else:
                for index in df2.index.get_level_values(0).unique():
                    fig.add_trace(
                    go.Scatter(
                    name="{} ({})".format(index,unit),
                    y=df2.loc[index].mean(),
                    x=df2.columns,
                    yaxis="y{}".format(index2+1)
                    ),
                )

    # if line > 1 view as boxplot
    # view as button: rollup 1 M, 1 Y, All
    # view as button: line, bar, statistical

    ################
    # LAYOUT
    ################
    r_domain = min(np.round(1.25 - (len(units)*.15),2), 1)
    fig.update_layout(
        xaxis=dict(
            domain=[0, r_domain]
        ),
        yaxis=dict(
            title="{}".format(titles[0]),
        ),
    )

    positionl = .3
    positionr = r_domain
    for i in range(2,len(units)+1):
        if i == 1:
            positionl = 0.3
            side = 'left'
            anchor = 'x'
            position = None
        elif i == 2:
            side = 'right'
            positionl = positionl - .15
            position = positionl
            anchor = 'x'
        else:
            side= 'right'
            positionr = positionr + .15
            position = positionr
            anchor = 'free'

        fig.update_layout(
            {'yaxis{}'.format(i): {'anchor': anchor,
                   'overlaying': 'y',
                   'position': position,
                   'side': side,
                   'title': {'text': '{}'.format(titles[i-1])}}
        }
        )
    fig.update_layout(xaxis_rangeslider_visible=False)

    if len(items) == 1:
        title="TIMESERIES; {}; {}".format(items[0], ", ".join(line.values))
    else:
        title="TIMESERIES; {}".format(", ".join(line.values))
    fig.update_layout(dict(
        title=title,
        xaxis={'rangeselector': {'buttons': list([{'count': 1, 'label': '1M', 'step': 'month', 'stepmode': 'backward'},
                                                  {'count': 6, 'label': '6M', 'step': 'month', 'stepmode': 'backward'},
                                                  {'step': 'all'}])}},
    ),
    )
    return fig


def make_bar_plot(relayoutData=None):
    data_filt = data
    start_str = end_str = None
    if relayoutData != None:
        if ("xaxis.autorange" not in relayoutData.keys()) &\
           ("autosize" not in relayoutData.keys()):
            if 'xaxis.range' in relayoutData.keys():
                start_str = relayoutData['xaxis.range'][0]
                end_str = relayoutData['xaxis.range'][1]
            elif "xaxis.range[0]" in relayoutData.keys():
                start_str = relayoutData["xaxis.range[0]"]
                end_str = relayoutData["xaxis.range[1]"]
            start_str = start_str.split(" ")[0]
            end_str = end_str.split(" ")[0]
            start_obj = datetime.datetime.strptime(start_str, '%Y-%m-%d')
            end_obj = datetime.datetime.strptime(end_str, '%Y-%m-%d')
            cols = [col for col in data.columns if (col >= start_obj) &
                                                    (col <= end_obj)]
            data_filt = data[cols]
        else:
            data_filt = data
    # create usage df
    df = data_filt.mean(axis=1).reorder_levels([2,1,0])
    df = pd.DataFrame(df).unstack()
    df = df.reorder_levels([1,0]).loc['GJ'][0].dropna(axis=1)
    df['Totals'] = df.sum(axis=1)
    df = df.sort_values(by='Totals')

    # create CO2/MT df
    df2 = pd.DataFrame(data_filt.mean(axis=1)).loc['CO2/production']
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
        title="OVERVIEW",
        # clickmode='event+select',
    ),
    )
    return fig

# Describe the layout/ UI of the app
app.layout = html.Div([
    dcc.Dropdown(
        options=[
            {"label": str(county), "value": str(county)} for county in axis_options
        ],
        value=['Electricity', 'Nat. Gas', 'Steam usage', 'CO2/production'],
        multi=True,
        id='dropdown'
    ),
    # dcc.Graph(id='year_plot',
    #           figure=make_year_plot()
    #           ),
    dcc.Graph(id='time_plot',
              figure=make_time_plot()
              ),
    dcc.Graph(id='bar_plot',
              figure=make_bar_plot()
              ),

    html.Pre(id='relayout-data'
              ),
        ],
        className="pretty_container"
        )

app.config.suppress_callback_exceptions = False

# Update page
# @app.callback(
#     Output('relayout-data', 'children'),
#     [Input('bar_plot', 'selectedData')])
# def display_relayout_data(relayoutData):
#     return json.dumps(relayoutData, indent=2)

@app.callback(
    Output('bar_plot', 'figure'),
    [Input('time_plot', 'relayoutData')])
def display_bar_data(relayoutData):
    return make_bar_plot(relayoutData)

@app.callback(
    Output('time_plot', 'figure'),
    [Input('bar_plot', 'clickData'),
     Input('bar_plot', 'selectedData'),
     Input('dropdown', 'value')]
)
def display_time_plot(barClickData, barSelectedData, dropdown):
    return make_time_plot(barClickData, barSelectedData, dropdown)

if __name__ == "__main__":
    app.run_server(debug=True)
