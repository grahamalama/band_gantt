# -*- coding: utf-8 -*-
from collections import defaultdict
from datetime import datetime

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.figure_factory as ff
import plotly.plotly as py
import requests
from dash.dependencies import Event, Input, Output, State

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children='Band Gantt'),

    html.Div(children='''
        A Gantt chart for bands.
    '''),

    html.Div(id='search', children=[
        dcc.Input(id='input', value='Search for a band', type='search'),
        html.Button(id='submit', type='submit', children='ok'),
    ]),
    html.Div(id='graph',children=[
        dcc.Graph(id='gantt', figure={})
    ],style={'marginLeft': 10})
])

@app.callback(
    Output(component_id='gantt', component_property='figure'),
    [],
    [State(component_id='input', component_property='value')],
    [Event('submit', 'click')]
)
def callback(band_name):
    band_search_results = requests.get(
        "https://musicbrainz.org/ws/2/artist?query={}&limit=10&fmt=json".format(band_name)
    ).json()

    try:
        band_id = band_search_results['artists'][0]['id']
    except:
        return "no artist found"

    band_info = requests.get(
        "https://musicbrainz.org/ws/2/artist/{}?inc=artist-rels&fmt=json".format(band_id)
    ).json()
    
    band_start_date = band_info['life-span']['begin']
    band_end_date = band_info['life-span']['ended'] if band_info['life-span']['ended'] else datetime.now()

    members = []

    for relation in band_info['relations']:
        if relation['type'] == 'member of band' or relation['type'] == "instrumental supporting musician":
            
            member = relation['artist']['name']
            start = relation['begin'] if relation['begin'] else band_start_date
            finish = relation['end'] if relation['end'] else band_end_date
            
            members.append({
                "Task": member,
                "Start": start,
                "Finish": finish 
            })

    fig = ff.create_gantt(members, group_tasks=True)
    
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
