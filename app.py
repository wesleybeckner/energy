# -*- coding: utf-8 -*-
import dash
import json
import dash_core_components as dcc
import dash_daq as daq
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

def make_gauge(relayoutData=None,
                 clickData=None,
                 selectedData=None):
    data_filt = data
    date_title = 'All Time'
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

            date_title = "{}, {} - {}, {}".format(start_obj.month,
                start_obj.year, end_obj.month, end_obj.year)
        else:
            data_filt = data
            date_title = 'All Time'
    if selectedData != None:
        line = pd.Series(pd.DataFrame.from_dict(selectedData['points'])['x'].unique())
    elif clickData != None:
        line = clickData['points'][0]['label']
    else:
        line = data.index.get_level_values(2).unique()
    if type(line) == str:
        line = pd.Series(line)
    items = ['Production', 'CO2']

    df = data_filt.loc[(data_filt.index.get_level_values(2).isin(line)) & # grab the right lines
             (data_filt.index.get_level_values(0).isin(items))]
    co2_prod = df.loc['CO2'].sum().sum() / df.loc['Production'].sum().sum()
    return co2_prod

def make_time_plot(clickData=None,
                   selectedData=None,
                   dropdown=None,
                   sample='Month',
                   plot_type='Scatter'):
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
            if sample == 'Year':
                df2 = df.T.resample('Y').sum().T
            else:
                df2 = df
            for index in df2.index.get_level_values(0).unique():
                # if plot_type == 'Scatter':
                #     fig.add_trace(
                #         go.Scatter(
                #         name=index,
                #         y=df2.loc[index].sum(),
                #         x=df2.columns,
                #         ),
                #         )
                # else:
                fig.add_trace(
                    go.Bar(
                    name=index,
                    y=df2.loc[index].sum(),
                    x=df2.columns,
                    ),
                    )
        else:
            if sample == 'Year':
                df2 = df.T.resample('Y').mean().T
            else:
                df2 = df
            for index in df2.index.get_level_values(0).unique():
                # if plot_type == 'Scatter':
                #     fig.add_trace(
                #     go.Scatter(
                #     name=index,
                #     y=df2.loc[index].mean(),
                #     x=df2.columns,
                #     ),
                #     )
                # else:
                fig.add_trace(
                go.Bar(
                name=index,
                y=df2.loc[index].mean(),
                x=df2.columns,
                ),
                )
    else:
        titles = []
        for index2, unit in enumerate(units):
            df2 = df.loc[(df.index.get_level_values(1) == unit)]
            titles.append("{}".format(df2.index.get_level_values(1).unique()[0]))
            if '/' not in unit: # sum Item values if no '/' otherwise take weight average
                if sample == 'Year':
                    df2 = df2.T.resample('Y').sum().T
                else:
                    df2 = df2
                for index in df2.index.get_level_values(0).unique():
                    if plot_type == 'Scatter':
                        fig.add_trace(
                        go.Scatter(
                        name="{} ({})".format(index,unit),
                        y=df2.loc[index].sum(),
                        x=df2.columns,
                        yaxis="y{}".format(index2+1)
                        ),
                        )
                    else:
                        fig.add_trace(
                        go.Bar(
                        name="{} ({})".format(index,unit),
                        y=df2.loc[index].sum(),
                        x=df2.columns,
                        yaxis="y{}".format(index2+1)
                        ),
                        )
            else:
                if sample == 'Year':
                    df2 = df2.T.resample('Y').mean().T
                else:
                    df2 = df2
                for index in df2.index.get_level_values(0).unique():
                    if plot_type == 'Scatter':
                        fig.add_trace(
                        go.Scatter(
                        name="{} ({})".format(index,unit),
                        y=df2.loc[index].mean(),
                        x=df2.columns,
                        yaxis="y{}".format(index2+1)
                        ),
                        )
                    else:
                        fig.add_trace(
                        go.Bar(
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
    r_domain = min(1.25 - (len(units)*.125), .95)
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
            positionr = positionr + .1
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
        barmode="stack",
        xaxis={'rangeselector': {'buttons': list([{'count': 1, 'label': '1M', 'step': 'month', 'stepmode': 'backward'},
                                                  {'count': 6, 'label': '6M', 'step': 'month', 'stepmode': 'backward'},
                                                  {'step': 'all'}])}},


    ),
    )
    fig.update_layout({
                "plot_bgcolor": "#F9F9F9",
                "paper_bgcolor": "#F9F9F9",
    })
    return fig

def make_bar_plot_delta(relayoutData=None,
                         dropdown=None,):
    # time filter
    data_filt = data
    date_title = 'All Time'
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

            date_title = "{}, {} - {}, {}".format(start_obj.month,
                start_obj.year, end_obj.month, end_obj.year)
        else:
            data_filt = data
            date_title = 'All Time'

    # item filter
    if dropdown != None:
        items = [dropdown[-1]]
    else:
        items = ['Electricity', 'Nat. Gas', 'Steam usage']
        items = ['CO2/production']

    df = data_filt.loc[(data_filt.index.get_level_values(0).isin(items))]

    units = df.index.get_level_values(1).unique() # detect number of different unit types; compute axes

    fig = go.Figure()
    colors = [
        '#1f77b4',  # muted blue
        '#ff7f0e',  # safety orange
        '#2ca02c',  # cooked asparagus green
        '#d62728',  # brick red
        '#9467bd',  # muted purple
        '#8c564b',  # chestnut brown
        '#e377c2',  # raspberry yogurt pink
        '#7f7f7f',  # middle gray
        '#bcbd22',  # curry yellow-green
        '#17becf'   # blue-teal
    ]

    titles = ["{}".format(df.index.get_level_values(1).unique()[0])]
    df2 = df.reorder_levels([0,2,1])
    for index in df2.index.get_level_values(0).unique():
        y=df2.loc[index][df2.columns[-1]] - df2.loc[index][df2.columns[0]]
        fig.add_trace(
            go.Bar(
            name=index,
            y=y,
            x=df2.loc[index].index.get_level_values(0),
            ),
            )

    ################
    # LAYOUT
    ################
    r_domain = min(1.25 - (len(units)*.125), .95)

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
            positionr = positionr + .1
            position = positionr
            anchor = 'free'

        if position > 1:
            position = 1
        fig.update_layout(
            {'yaxis{}'.format(i): {'anchor': anchor,
                   'overlaying': 'y',
                   'position': position,
                   'side': side,
                   'title': {'text': '{}'.format(titles[i-1])}
                                  }
        }
        )
    if len(items) == 1:
        title="{}, By Site, {}".format(items[0], date_title)
    else:
        title="By Site: {}".format(date_title)
    fig.update_layout(dict(
        title=title,
        barmode="group",
    ),
    )
    fig.update_layout({
                "plot_bgcolor": "#F9F9F9",
                "paper_bgcolor": "#F9F9F9",
    })
    return fig

def make_bar_plot_single(relayoutData=None,
                         dropdown=None,):
    # time filter
    data_filt = data
    date_title = 'All Time'
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

            date_title = "{}, {} - {}, {}".format(start_obj.month,
                start_obj.year, end_obj.month, end_obj.year)
        else:
            data_filt = data
            date_title = 'All Time'

    # item filter
    if dropdown != None:
        items = [dropdown[-1]]
    else:
        items = ['Electricity', 'Nat. Gas', 'Steam usage']
        items = ['CO2/production']

    df = data_filt.loc[(data_filt.index.get_level_values(0).isin(items))]

    units = df.index.get_level_values(1).unique() # detect number of different unit types; compute axes

    fig = go.Figure()
    colors = [
        '#1f77b4',  # muted blue
        '#ff7f0e',  # safety orange
        '#2ca02c',  # cooked asparagus green
        '#d62728',  # brick red
        '#9467bd',  # muted purple
        '#8c564b',  # chestnut brown
        '#e377c2',  # raspberry yogurt pink
        '#7f7f7f',  # middle gray
        '#bcbd22',  # curry yellow-green
        '#17becf'   # blue-teal
    ]
    if len(units) == 1:
        titles = ["{}".format(df.index.get_level_values(1).unique()[0])]
        df2 = df.reorder_levels([0,2,1])
        for index in df2.index.get_level_values(0).unique():
            if '/' not in units: # sum Item values if no '/' otherwise take weight average
                y=df2.loc[index].sum(axis=1)
            else:
                y=df2.loc[index].mean(axis=1)
            fig.add_trace(
                go.Bar(
                name=index,
                y=y,
                x=df2.loc[index].index.get_level_values(0),
                ),
                )

    ################
    # LAYOUT
    ################
    r_domain = min(1.25 - (len(units)*.125), .95)

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
            positionr = positionr + .1
            position = positionr
            anchor = 'free'

        if position > 1:
            position = 1
        fig.update_layout(
            {'yaxis{}'.format(i): {'anchor': anchor,
                   'overlaying': 'y',
                   'position': position,
                   'side': side,
                   'title': {'text': '{}'.format(titles[i-1])}
                                  }
        }
        )
    if len(items) == 1:
        title="{}, By Site, {}".format(items[0], date_title)
    else:
        title="By Site: {}".format(date_title)
    fig.update_layout(dict(
        title=title,
        barmode="group",
    ),
    )
    fig.update_layout({
                "plot_bgcolor": "#F9F9F9",
                "paper_bgcolor": "#F9F9F9",
    })
    return fig

def make_bar_plot_multiple(relayoutData=None,
                  dropdown=None,):
    # time filter
    data_filt = data
    date_title = 'All Time'
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

            date_title = "{}, {} - {}, {}".format(start_obj.month,
                start_obj.year, end_obj.month, end_obj.year)
        else:
            data_filt = data
            date_title = 'All Time'

    # item filter
    if dropdown != None:
        items = dropdown
    else:
        items = ['Electricity', 'Nat. Gas', 'Steam usage']
        items = items + ['CO2/production']

    df = data_filt.loc[(data_filt.index.get_level_values(0).isin(items))]

    units = df.index.get_level_values(1).unique() # detect number of different unit types; compute axes

    fig = go.Figure()
    colors = [
        '#1f77b4',  # muted blue
        '#ff7f0e',  # safety orange
        '#2ca02c',  # cooked asparagus green
        '#d62728',  # brick red
        '#9467bd',  # muted purple
        '#8c564b',  # chestnut brown
        '#e377c2',  # raspberry yogurt pink
        '#7f7f7f',  # middle gray
        '#bcbd22',  # curry yellow-green
        '#17becf'   # blue-teal
    ]
    # if len(units) == 1:
    #     titles = ["{}".format(df.index.get_level_values(1).unique()[0])]
    #     df2 = df.reorder_levels([0,2,1])
    #     for index in df2.index.get_level_values(0).unique():
    #         if '/' not in units: # sum Item values if no '/' otherwise take weight average
    #             y=df2.loc[index].sum(axis=1)
    #         else:
    #             y=df2.loc[index].mean(axis=1)
    #         fig.add_trace(
    #             go.Bar(
    #             name=index,
    #             y=y,
    #             x=df2.loc[index].index.get_level_values(0),
    #             ),
    #             )
    # else:
    titles = []
    for index2, unit in enumerate(units):
        df2 = df.loc[(df.index.get_level_values(1) == unit)]
        df2 = df2.reorder_levels([2,0,1])
        titles.append("{}".format(df2.index.get_level_values(2).unique()[0]))
        for ind, index in enumerate(df2.index.get_level_values(0).unique()):
            if index2 > 0:
                showlegend=False
            else:
                showlegend=True
            yaxis="y{}".format(index2+1)
            if '/' not in unit: # sum Item values if no '/' otherwise take weight average
                y=df2.loc[index].sum(axis=1)
            else:
                y=df2.loc[index].mean(axis=1)
            fig.add_trace(
            go.Bar(
            name="{}".format(index),
            y=y,
            x=df2.loc[index].index.get_level_values(0),
            legendgroup=index,
            yaxis=yaxis,
            marker_color=colors[ind],
            showlegend=showlegend,
            ),
            )

    ################
    # LAYOUT
    ################
    r_domain = min(1.25 - (len(units)*.125), .95)

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
            positionr = positionr + .1
            position = positionr
            anchor = 'free'

        if position > 1:
            position = 1
        fig.update_layout(
            {'yaxis{}'.format(i): {'anchor': anchor,
                   'overlaying': 'y',
                   'position': position,
                   'side': side,
                   'title': {'text': '{}'.format(titles[i-1])}
                                  }
        }
        )
    if len(items) == 1:
        title="{}, By Site, {}".format(items[0], date_title)
    else:
        title="By Site: {}".format(date_title)
    fig.update_layout(dict(
        title=title,
        barmode="group",
    ),
    )
    fig.update_layout({
                "plot_bgcolor": "#F9F9F9",
                "paper_bgcolor": "#F9F9F9",
    })
    return fig

# Describe the layout/ UI of the app
app.layout = html.Div([
html.Div([
html.Div([
    dcc.Dropdown(
        options=[
            {"label": str(county), "value": str(county)} for county in axis_options
        ],
        value=['Electricity', 'Nat. Gas', 'Steam usage', 'CO2/production'],
        multi=True,
        id='dropdown'),
    dcc.RadioItems(
                id='sample',
                options=[{'label': i, 'value': i} for i in ['Month', 'Year']],
                value='Month',
                labelStyle={'display': 'inline-block'}),
            ], className="twelve columns"
            ),

        html.Div([
            dcc.Graph(id='time_plot',
                      figure=make_time_plot()
                      ),
                  ], className="eight columns"
                  ),
        html.Div([
            dcc.Graph(id='bar_plot_single',
                      figure=make_bar_plot_single()
                      ),
                ], className="four columns"
                ),
            ], style={'min-width': '1100px',
                    'max-width': '1500px'},
                className="pretty container"
            ),
    html.Div([
        html.Div([
            daq.Gauge(
                id='my-gauge',
                label="CO2/production",
                value=0.16,
                max=1,
                min=0,
                color={"gradient":True,"ranges":{"green":[0,.6],"yellow":[.6,.8],"red":[.8,1]}}),
                ], className="four columns",
                style={'display': 'inline-block',
                       'margin-top': '70px',
                       "background-color": "#F9F9F9",

                       },
                ),
        html.Div([
        dcc.Graph(id='bar_plot_delta',
                  figure=make_bar_plot_delta()
                  ),
            ],
            className="eight columns"
            ),
            ],style={'min-width': '1100px',
                    'max-width': '1500px',
                    "background-color": "#F9F9F9"},
                    className="pretty container"
            ),
    html.Div([
    html.Div([
        dcc.Graph(id='bar_plot_multiple',
                  figure=make_bar_plot_multiple()
                  ),
                  ], className='twelve columns'
                  ),
                  ], style={'min-width': '1100px',
                          'max-width': '1500px'},
                  className='pretty container'
                  ),



        html.Pre(id='relayout-data'),

        ]
        )

app.config.suppress_callback_exceptions = False

# Update page
# @app.callback(
#     Output('relayout-data', 'children'),
#     [Input('bar_plot_single', 'selectedData')])
# def display_relayout_data(selectedData):
#     return json.dumps(selectedData, indent=2)
@app.callback(
    Output('my-gauge', 'value'),
    [Input('time_plot', 'relayoutData'),
     Input('bar_plot_single', 'clickData'),
     Input('bar_plot_single', 'selectedData')]
)
def update_gauge(relayoutData, clickData, selectedData):
    return make_gauge(relayoutData, clickData, selectedData)
@app.callback(
    Output('bar_plot_single', 'figure'),
    [Input('time_plot', 'relayoutData'),
     Input('dropdown', 'value')])
def display_bar_data(relayoutData, dropdown):
    return make_bar_plot_single(relayoutData, dropdown)
@app.callback(
    Output('bar_plot_multiple', 'figure'),
    [Input('time_plot', 'relayoutData'),
     Input('dropdown', 'value')])
def display_bar_data(relayoutData, dropdown):
    return make_bar_plot_multiple(relayoutData, dropdown)
@app.callback(
    Output('bar_plot_delta', 'figure'),
    [Input('time_plot', 'relayoutData'),
     Input('dropdown', 'value')])
def display_bar_delta(relayoutData, dropdown):
    return make_bar_plot_delta(relayoutData, dropdown)
@app.callback(
    Output('time_plot', 'figure'),
    [Input('bar_plot_single', 'clickData'),
     Input('bar_plot_single', 'selectedData'),
     Input('dropdown', 'value'),
     Input('sample', 'value')]
)
def display_time_plot(barClickData, barSelectedData, dropdown, sample):
    return make_time_plot(barClickData, barSelectedData, dropdown, sample)

if __name__ == "__main__":
    app.run_server(debug=True)
