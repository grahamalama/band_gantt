# -*- coding: utf-8 -*-
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

app.layout = html.Div(children=[
    dcc.Location(id='url', refresh=False),
    html.H1(children='Band Gantt'),

    html.Div(children='''
        A Gantt chart for bands.
    '''),
    html.Div(children=[
        html.Div([
            html.Label('Band Name'),
            dcc.Input(
                id='band_search',
                placeholder='Enter a band name...',
                type='text',
                value=''
            )
        ]),
        html.Div(
            id='search_results', children=[]
        )
    ], style={'float': 'left'}),

    html.Div(id='graph', children=[
        dcc.Graph(id='gantt', figure={})
    ], style={'float': 'right'})

])


@app.callback(
    Output(component_id='search_results', component_property='children'),
    [Input(component_id='band_search', component_property='value')]
)
def search_for_band(query_string):
    if len(query_string) > 3:
        band_search_results = requests.get(
            "https://musicbrainz.org/ws/2/artist?query={}&limit=10&fmt=json".format(
                query_string)
        ).json()

        formatted_results = []
        for artist in band_search_results['artists']:
            formatted_results.append(
                html.Span(children=[
                    html.A(href=artist['id'], children=artist['name']),
                    html.Br()
                ])
            )

        return formatted_results


@app.callback(
    Output(component_id='gantt', component_property='figure'),
    [Input(component_id='url', component_property='pathname')]
)
def create_graph(pathname):
    # removes leading slash in pathname
    artist_id = pathname[1:]
    band_info = requests.get(
        "https://musicbrainz.org/ws/2/artist/{}?inc=artist-rels&fmt=json".format(
            artist_id)
    ).json()

    members = band_member_dict(band_info)
    band_member_names = set([member['Resource'] for member in members])
    
    fig_colors = variable_color_scale(len(band_member_names))
    fig_colors_dict = dict(zip(band_member_names, fig_colors))

    fig = ff.create_gantt(df=members, colors=fig_colors_dict, group_tasks=True,
                          index_col='Resource')
    return fig


def band_member_dict(band_info):
    '''returns a dict of band member info in a format useful for generating a 
    plotly Gantt chart'''

    band_start_date = band_info['life-span']['begin']

    if band_info['life-span']['ended']:
        band_end_date = band_info['life-span']['ended']
    else:
        band_end_date = datetime.now()

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
