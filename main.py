# -*- coding: utf-8 -*-
import sys

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import plotly.graph_objects as go
import knowledge_network as kn


#===============================================================================
# basic stuff & global variables

# load external syle cheet (css)
#external_stylesheets = ['style.css']#['https://codepen.io/chriddyp/pen/bWLwgP.css']

# create dash app
app = dash.Dash(__name__) #, external_stylesheets=external_stylesheets)

# check if running in local mode (-l)
if not "-local" in sys.argv:
    server = app.server

if "-kiwix" in sys.argv:
    base_url = "http://192.168.0.9:8181/7fe4cca9-607f-5932-c685-9a22c1c410b5/A/"
    local = True
else:
    base_url = "https://en.wikipedia.org/wiki/"
    local = False

# define graph graph object
graph = None
start_layout = 'kamada_kawai_layout'

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
# Define App Layout

app.layout = html.Div(className="app",
    children = [
    html.Div(className="header", children = [
    html.H1("Wikipedia Link Graph"),
    html.P("This app generates a graph based on links between Wikipedia articles. "),
    html.P(["You can determine the article to start with.",
    " All linked articles in the article's summary will be added to the graph. ",
    "If the depth is greater than one, the links of the linked articles will be added and so on ... ",
    html.Br(),
    "The graph shows all articles as bubbles and all links as lines."]),
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
        value=start_layout),
    dcc.Markdown(id='text_output')
    ])
])



#===============================================================================
# Callbacks - Interaktion mit der Benutzeroberfläche

# Mit @ wird ein sogenannter "Decorater" benutzt.
# Der Decorator führt dazu, dass die Funktion, die darunter deklariert wird
# (hier update_output) die Funktionalität des Decorators erhält.
# Hier werden Input, Output, State vom Paket dash.dependencies verwendet (siehe import).
# Wichtig ist, dass Inputs und Outputs mit den Argumenten und Returns der Funktion zusammenpassen!


@app.callback(Output('text_output', 'children'),
              Input('start_button', 'n_clicks'),
              State('topic', 'value'),
              State('depth', 'value'))

def check_if_article_exists(n_clicks, topic, depth):
    global graph
    graph = kn.KnowledgeGraph(topic, depth, start_layout, base_url, local)

    if graph.topic:
        output = '''
            The current topic is **{}**
            and the depth of the network is **{}**.
        '''.format(topic, depth)

    else:
        output = "**Topic does not exist.**"

    return output


@app.callback(Output('knowledge-graph', 'figure'),
              Input('text_output', 'children'),
              Input('layout_dropdown', 'value'),
              State('knowledge-graph', 'figure'),
              State('layout_dropdown', 'value'))

def update_figure(text, dropdown, figure, layout):
    #print(text, dropdown, figure, layout)
    ctx = dash.callback_context
    input_id = ctx.triggered[0]["prop_id"].split(".")[0]
    global graph

    if input_id == "layout_dropdown":
        graph.layout = ctx.triggered[0]["value"]
        figure['data'] = graph.display()
        display = 'Changing to ' + layout
        return figure
    else:
        if text == '**Topic does not exist.**':
            figure['data'] = None
        else:
            graph.build()
            figure['data'] = graph.display()

        return figure


#===============================================================================
# Server starten

if __name__ == '__main__':
    app.run_server(debug=True, port = 8000)
