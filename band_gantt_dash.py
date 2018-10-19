# -*- coding: utf-8 -*-
import os
import random
from collections import defaultdict
from datetime import datetime

import colorlover as cl
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.figure_factory as ff
import requests
from dash.dependencies import Input, Output

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

app.layout = html.Div(children=[
    dcc.Location(id='url', refresh=False),
    html.Div(children=[
        
        html.Div(children=[    
            html.H1(children='Band Gantt'),
            html.Div(children=[
                html.Div([
                    dcc.Input(
                        id='band_search',
                        placeholder='Enter a band name...',
                        type='text',
                        value=''
                    )
                ]),
                html.Div(
                    id='search_results', 
                    children=[],
                    style={
                        'background-color': "#fcfcfc",
                        'border-radius': '20px',
                        'zIndex':'1',
                        'position':'absolute'
                    }
                )
            ]),
        ]),

        html.Div(id='graph', children=[], className="twelve columns")

    ],className="row")     
])


@app.callback(
    Output(component_id='search_results', component_property='children'),
    [Input(component_id='band_search', component_property='value')]
)
def search_for_band(query_string):
    if len(query_string) > 2:
        band_search_results = requests.get(
            "https://musicbrainz.org/ws/2/artist?query={}&limit=10&fmt=json".format(
                query_string + '*')
        ).json()

        formatted_results = []
        for artist in band_search_results['artists']:
            formatted_results.append(
                html.Span(children=[
                    dcc.Link(artist['name'], href=artist['id']),
                    html.Br()
                ])
            )

        return formatted_results

@app.callback(
    Output(component_id='band_search', component_property='value'),
    [Input(component_id='url', component_property='pathname')]
)
def clear_search_bar(pathname):
    return ''


@app.callback(
    Output(component_id='graph', component_property='children'),
    [Input(component_id='url', component_property='pathname')]
)
def create_graph(pathname):
    
    if pathname == "/":
        # A few example bands to generate at random when the app opens
        example_ids = [ 
            'b10bbbfc-cf9e-42e0-be17-e2c3e1d2600d', # The Beatles
            'c1d4f2ba-cf39-460c-9528-6b827d3417a1', # Yes
            'eeb1195b-f213-4ce1-b28c-8565211f8e43', # Guns N' Roses 
            '36bfa85f-737b-41db-a8fc-b8825850ffc3', # Pavement
        ]
        
        artist_id = random.choice(example_ids)
    else:
        artist_id = pathname[1:] # removes leading slash in pathname

    band_info = requests.get(
        "https://musicbrainz.org/ws/2/artist/{}?inc=artist-rels&fmt=json".format(
            artist_id)
    ).json()

    members = band_member_dict(band_info)
    if members:
        band_start_date, band_end_date  = start_and_end_date(band_info)
        band_member_names = set([member['Resource'] for member in members])
        
        fig_colors = variable_color_scale(len(band_member_names))
        fig_colors_dict = dict(zip(band_member_names, fig_colors))

        fig = ff.create_gantt(df=members, colors=fig_colors_dict, group_tasks=True,
                            index_col='Resource', title=band_info['name'])
        fig = customize_gantt(fig,band_start_date,band_end_date)
        return dcc.Graph(
                id='gantt', 
                figure=fig,
                config={'displayModeBar': False}
            )
    else:
        return html.H3("No band member information available.")

def customize_gantt(gantt_fig,start_date,end_date):
    '''Make changes to figure generated from create_gantt()'''

    del gantt_fig['layout']['xaxis']['rangeselector']
    del gantt_fig['layout']['height']
    del gantt_fig['layout']['width'] 
    gantt_fig['layout']['autosize'] = True
    gantt_fig['layout']['xaxis']['autorange'] = True
    gantt_fig['layout']['yaxis']['autorange'] = True
    gantt_fig['layout']['margin'] =  dict(r=10,t=100,b=50,l=150)

    return gantt_fig

def start_and_end_date(band_info):
    band_start_date = band_info['life-span']['begin']

    if band_info['life-span']['ended'] == True:
        band_end_date = band_info['life-span']['end']
    else:
        band_end_date = datetime.now()
    return (band_start_date,band_end_date)

def band_member_dict(band_info):
    '''returns a dict of band member info in a format useful for generating a 
    plotly Gantt chart'''

    band_start_date, band_end_date  = start_and_end_date(band_info)

    members = []
    for relation in band_info['relations']:
        if relation['type'] in ['member of band', 'instrumental supporting musician']:

            member = relation['artist']['name']
            start = relation['begin'] if relation['begin'] else band_start_date
            finish = relation['end'] if relation['end'] else band_end_date

            members.append({
                "Task": member,
                "Start": start,
                "Finish": finish,
                "Resource": member
            })

    return members


def variable_color_scale(band_size):
    '''returns a color scale that accomodates bands smaller than 2 members and
       larger than 12 members'''
    colors = cl.scales['12']['qual']['Paired'] * (band_size // 12 + 1)
    colors = colors[: 12 - (band_size % 12 + 1):-1]
    return colors


if __name__ == '__main__':
    app.run_server(debug=True)
