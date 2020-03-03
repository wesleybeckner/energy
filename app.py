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
    date_title = ''
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
            date_title = ''
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
        items = ['Electricity', 'Nat. Gas', 'Steam usage', 'Energy Intensity']
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
        title="{}; Lines: {}".format(items[0], ", ".join(line.values))
    else:
        title="Lines: {}".format(", ".join(line.values))
    fig.update_layout(dict(
        title=title,
        barmode="stack",
        xaxis={'rangeselector': {'buttons': list([{'count': 1, 'label': '1M', 'step': 'month', 'stepmode': 'backward'},
                                                  {'count': 3, 'label': '3M', 'step': 'month', 'stepmode': 'backward'},
                                                  {'count': 6, 'label': '6M', 'step': 'month', 'stepmode': 'backward'},
                                                  {'count': 1, 'label': '1Y', 'step': 'year', 'stepmode': 'backward'},
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
    date_title = ''
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
            date_title = ''

    # item filter
    if dropdown != None:
        items = [dropdown[-1]]
    else:
        items = ['Electricity', 'Nat. Gas', 'Steam usage']
        items = ['Energy Intensity']

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
        title="{} Delta, By Site {}".format(items[0], date_title)
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
    date_title = ''
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
            date_title = ''

    # item filter
    if dropdown != None:
        items = [dropdown[-1]]
    else:
        items = ['Electricity', 'Nat. Gas', 'Steam usage']
        items = ['Energy Intensity']

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
            if '/' not in units[0]: # sum Item values if no '/' otherwise take weight average
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
        title="{}, By Site {}".format(items[0], date_title)
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
    date_title = ''
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
            date_title = ''

    # item filter
    if dropdown != None:
        items = dropdown
    else:
        items = ['Electricity', 'Nat. Gas', 'Steam usage']
        items = items + ['Energy Intensity']

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
        title="{}, By Site {}".format(items[0], date_title)
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

def calc_key_takeaways(relayoutData):
    # time filter
    data_filt = data
    start_str = end_str = None
    metrics = ["CO2", "Production", "Energy Intensity", "CO2/production"]
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

            #calculate totals for CO2, Energy, Production

            months = np.round((end_obj - start_obj).days/31)
            timedelta = (end_obj - start_obj)
            prev_period_start = start_obj - timedelta
            cols = [col for col in data.columns if (col <= start_obj) &
                                                            (col >= prev_period_start)]
            data_filt_prev = data[cols]

            prevs = []
            totals = []
            for index, met in enumerate(metrics):

                if ("/" not in met) and (" " not in met):
                    total = data_filt.loc[met].sum(axis=1).sum()
                    prev = data_filt_prev.loc[met].sum(axis=1).sum()
                else:
                    total = data_filt.loc[met].mean(axis=1).mean()
                    prev = data_filt_prev.loc[met].mean(axis=1).mean()
                unit =  data_filt.loc[met].index.get_level_values(0).unique()[0]

                percent = (total - prev) / prev * 100

                prevs.append("{:.2f}% since last {:.0f}mo".format(percent, months))
                totals.append("{:.2f} {}".format(total, unit))
            df = pd.DataFrame([totals,prevs])
            df.columns = metrics
    else:
        data_filt = data
        totals = []

        for index, met in enumerate(metrics):
            if ("/" not in met) and (" " not in met):
                totals.append(data_filt.loc[met].sum(axis=1).sum())
                # prevs.append(data_filt_prev.loc[met].sum(axis=1).sum())
            else:
                totals.append(data_filt.loc[met].mean(axis=1).mean())
                # prevs.append(data_filt_prev.loc[met].mean(axis=1).mean())
        df = pd.DataFrame([totals])
        df.columns = metrics

    return df

# Describe the layout/ UI of the app
app.layout = html.Div([
# html.Div([
# html.Div([
html.Div([
html.Div([
html.Div(
                            [
                                html.Div(
                                    [html.H6(id="co2_text"), html.P("CO2"),
                                    html.P(id="co2_percent")],
                                    id="co2",
                                    style={
                                    'min-width': '190px',
                                    'max-width': '400px',
                                    },
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6(id="production_text"), html.P("Production"),
                                    html.P(id="production_percent")],
                                    id="production",
                                    style={
                                    'min-width': '190px',
                                    'max-width': '400px',
                                    },
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6(id="energy_text"), html.P("Energy Intensity"),
                                    html.P(id="energy_percent")],
                                    id="energy",
                                    style={
                                    'min-width': '190px',
                                    'max-width': '400px',
                                    },
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6(id="ratio_text"), html.P("CO2/Production"),
                                    html.P(id="ratio_percent")],
                                    id="ratio",
                                    style={
                                    'min-width': '190px',
                                    'max-width': '400px',
                                    },
                                    className="mini_container",
                                ),
                            ],
                            id="info-container",
                            className="row container-display",
                            # style={'max-width': '1600px'},
                        ),
                #         ],
                #     id="top-column",
                #     className="twelve columns",
                # ),
#             ],
#             className="row flex-display",
#         ),
                html.Div([
html.Div([
                    # html.Div([
                    dcc.Graph(id='bar_plot_delta',
                              figure=make_bar_plot_delta()
                              ),
                              ],
                              className="six columns",
                              ),
                              # ],
                              # className="pretty container",
                              # ),

                    # html.Div([
                    html.Div([
                        dcc.Graph(id='bar_plot_single',
                                  figure=make_bar_plot_single()
                                  ),
                            ],className="six columns"
                                # style={'margin-top': '50px',
                                #         'margin-left': '10px',}
                            ),
                            # ],
                            # className="pretty container",
                            # ),
                            ],
                            className="row flex-display",
                            ),
                        ],
                        className="pretty container"
                        ),
                        ],
                        # style={'min-width': '1100px',
                        #         'max-width': '1500px'},
                                # "background-color": "#F9F9F9"},
                                className="row flex-display",
                                # style={'max-width': '1600px'},
                        ),


            # ],
            # style={'min-width': '1200px',
            #         'max-width': '1600px',
            #     # "background-color": "#F9F9F9"
                # },
            #     className="pretty container"
            # ),
    # html.Div([
    #     daq.Gauge(
    #         id='my-gauge',
    #         label="CO2/production",
    #         value=0.16,
    #         max=1,
    #         min=0,
    #         color={"gradient":True,"ranges":{"green":[0,.6],"yellow":[.6,.8],"red":[.8,1]}}),
    #         ], className="four columns",
    #         style={'display': 'inline-block',
    #                'margin-top': '70px',
    #                # "background-color": "#F9F9F9",
    #
    #                },
    #         ),

    html.Div([
        html.Div([
            html.Div([
            dcc.Dropdown(
                options=[
                    {"label": str(county), "value": str(county)} for county in axis_options
                ],
                value=['Electricity', 'Nat. Gas', 'Steam usage', 'Energy Intensity'],
                multi=True,
                id='dropdown'),
            dcc.RadioItems(
                        id='sample',
                        options=[{'label': i, 'value': i} for i in ['Month', 'Year']],
                        value='Month',
                        labelStyle={'display': 'inline-block'}),
                        ],
                        className='mini_container',
                        ),
            dcc.Graph(id='time_plot',
                      figure=make_time_plot()
                      ),
                  ], className="twelve columns"
                  ),

                  ],
                  # style={'min-width': '1200px',
                  #         'max-width': '1600px'},
                     className = "pretty container",
                  ),
    # html.Div([
    # html.Div([
    #     dcc.Graph(id='bar_plot_multiple',
    #               figure=make_bar_plot_multiple()
    #               ),
    #               ], className='twelve columns'
    #               ),
    #               ], style={'min-width': '1100px',
    #                       'max-width': '1500px'},
    #               className='pretty container'
    #               ),



        html.Pre(id='relayout-data'),

        ],
        id="mainContainer",
        style={"display": "flex", "flex-direction": "column"},
        )

app.config.suppress_callback_exceptions = False

# Update page
# @app.callback(
#     Output('relayout-data', 'children'),
#     [Input('bar_plot_single', 'selectedData')])
# def display_relayout_data(selectedData):
#     return json.dumps(selectedData, indent=2)
# @app.callback(
#     Output('my-gauge', 'value'),
#     [Input('time_plot', 'relayoutData'),
#      Input('bar_plot_single', 'clickData'),
#      Input('bar_plot_single', 'selectedData')]
# )
# def update_gauge(relayoutData, clickData, selectedData):
#     return make_gauge(relayoutData, clickData, selectedData)
@app.callback(
    [Output('co2_text', 'children'),
    Output('co2_percent', 'children')],
    [Input('time_plot', 'relayoutData')])
def update_met1(relayoutData):
    df = calc_key_takeaways(relayoutData)
    value1 = df[df.columns[0]].values[0]
    value2 = df[df.columns[0]].values[1]
    return value1, value2
@app.callback(
    [Output('production_text', 'children'),
    Output('production_percent', 'children')],
    [Input('time_plot', 'relayoutData')])
def update_met1(relayoutData):
    df = calc_key_takeaways(relayoutData)
    value1 = df[df.columns[1]].values[0]
    value2 = df[df.columns[1]].values[1]
    return value1, value2
@app.callback(
    [Output('energy_text', 'children'),
    Output('energy_percent', 'children')],
    [Input('time_plot', 'relayoutData')])
def update_met1(relayoutData):
    df = calc_key_takeaways(relayoutData)
    value1 = df[df.columns[2]].values[0]
    value2 = df[df.columns[2]].values[1]
    return value1, value2
@app.callback(
    [Output('ratio_text', 'children'),
    Output('ratio_percent', 'children')],
    [Input('time_plot', 'relayoutData')])
def update_met1(relayoutData):
    df = calc_key_takeaways(relayoutData)
    value1 = df[df.columns[3]].values[0]
    value2 = df[df.columns[3]].values[1]
    return value1, value2

@app.callback(
    Output('bar_plot_single', 'figure'),
    [Input('time_plot', 'relayoutData'),
     Input('dropdown', 'value')])
def display_bar_data(relayoutData, dropdown):
    return make_bar_plot_single(relayoutData, dropdown)
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
# @app.callback(
#     Output('bar_plot_multiple', 'figure'),
#     [Input('time_plot', 'relayoutData'),
#      Input('dropdown', 'value')])
# def display_bar_data(relayoutData, dropdown):
#     return make_bar_plot_multiple(relayoutData, dropdown)

if __name__ == "__main__":
    app.run_server(debug=True)
