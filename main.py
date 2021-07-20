# -*- coding: utf-8 -*-
import sys

import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import plotly.graph_objects as go
import wiki_network


#===============================================================================
# basic stuff & global variables

# create dash app
app = dash.Dash(__name__)

# check if running in local mode (-local)
if not "-local" in sys.argv:
    server = app.server

if "-kiwix" in sys.argv:
    base_url = "http://192.168.0.9:8181/7fe4cca9-607f-5932-c685-9a22c1c410b5/A/"
    local = True
else:
    base_url = "https://en.wikipedia.org/wiki/"
    local = False


#===============================================================================
# generate and style figure

fig = go.Figure(data = None,  # hier wird die Funktion von oben benutzt
                layout=go.Layout(
                #height=900, width=1200,
                showlegend=False,
                hovermode='closest',
                margin=dict(b=5,l=5,r=5,t=40), # ab hier nur Styling
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                )


#===============================================================================
# define app layout

app.layout = html.Div(className="app",
    children = [
    html.Div(className="header", children = [
    html.H1("Wikipedia Link Graph"),
    html.P("This app generates a graph based on links between Wikipedia articles. "),
    html.P(["You can determine the article to start with.",
    " All linked articles in the article's summary will be added to the graph. ",
    "If the depth is greater than one, the links of the linked articles will be added, and so on ... ",
    html.Br(),
    "The figure shows all articles as bubbles and all links as lines."]),
    ]),
    html.Div(className = "input-container", children =[
    dcc.Input(className="input", id='topic', type='text', value='Python (programming language)',\
              placeholder="topic"),
    dcc.Input(className="input", id='depth', type='number', value=2,\
              placeholder="search depth"),
    html.Button(className="input", id='start_button', n_clicks=0, children='Start')
    ]),
    html.Div(className="graph", children = [
    dcc.Graph(
        id='knowledge-graph',
        figure=fig
    ),
    dcc.Dropdown(
        id='layout_dropdown',
        options=[
            {'label': 'Kamada Kawai Layout', 'value': 'kamada_kawai_layout'},
            {'label': 'Shell Layout', 'value': 'shell_layout'},
            {'label': 'Spring Layout', 'value': 'spring_layout'},
            {'label': 'Spectral Layout', 'value': 'spectral_layout'},
            {'label': 'Spiral Layout', 'value': 'spiral_layout'}
        ],
        value='kamada_kawai_layout'),
    dcc.Markdown(id='summary', style = {'color' : 'black'}),
    dash_table.DataTable(id='table',
    columns=[{"name": "param", "id": "param"}, {"name": "value", "id": "value"}],
    data= [
        	{"param": "topic", 'value': None},
            {"param": "depth", 'value': None},
            {"param": "slug", 'value': None}]),
    dcc.Store(id='graph_container')
    ]),
])


#===============================================================================
# callbacks

@app.callback(Output('summary', 'children'),
              Output('summary', 'style'),
              Output('table', 'data'),
              Input('start_button', 'n_clicks'),
              State('topic', 'value'),
              State('depth', 'value'))

def check_if_article_exists(n_clicks, topic, depth):
    article, slug = wiki_network.valid_article(topic)
    if article:
        summary = '''
            Building graph around **{}** with depth **{}**.
            This can take a while!
        '''.format(article, depth)
        style = {'color' : 'black'}
        data = [{'param': 'topic', 'value': article},
                {'param': 'depth', 'value': depth},
                {'param': 'slug', 'value': slug}]
    else:
        summary = "**Topic does not exist.**"
        style = {'color' : 'red'}
        data= [
            	{"param": "topic", 'value': None},
                {"param": "depth", 'value': None},
                {"param": "slug", 'value': None}]

    return summary, style, data


@app.callback(Output('knowledge-graph', 'figure'),
              Output('graph_container', 'data'),
              Input('table', 'data'),
              Input('layout_dropdown', 'value'),
              State('knowledge-graph', 'figure'),
              State('layout_dropdown', 'value'),
              State('graph_container', 'data'))

def update_figure(data, dropdown, figure, layout, json_data):
    ctx = dash.callback_context
    input_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if input_id == "layout_dropdown":
        figure['data'] = wiki_network.display(json_data, ctx.triggered[0]["value"])
        return figure, json_data

    else:
        if data[0]['value'] == None:
            figure['data'] = None
            json_graph = None
        else:
            json_graph = wiki_network.build(data[0]['value'], data[1]['value'], data[2]['value'], local, base_url)
            figure['data'] = wiki_network.display(json_graph, layout)

        return figure, json_graph


#===============================================================================
# start server

if __name__ == '__main__':
    app.run_server(debug=True, port = 8000)
