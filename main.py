# -*- coding: utf-8 -*-
import sys
import time

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import plotly.graph_objects as go
import knowledge_network as kn



#===============================================================================
# basic stuff & global variables

# load external syle cheet (css)
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# create dash app
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# check if running in local mode (-l)
if not "-l" in sys.argv:
    server = app.server
else:
    print("Running in local mode.")

# define graph graph object
graph = None
sanity_check = False

#===============================================================================
# generate and style figure

fig = go.Figure(data = None,  # hier wird die Funktion von oben benutzt
                layout=go.Layout(
                height=900, width=1200,
                showlegend=False,
                hovermode='closest',
                margin=dict(b=5,l=5,r=5,t=40), # ab hier nur Styling
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                )

#===============================================================================
# Define App Layout

app.layout = html.Div([
    html.H1("Wikipedia Link Graph"),
    html.P("This app generates a graph, starting from one wikipedia page, \
    'klicking' all the links in the article's summary and does the same with the\
    linked articles. The graph shows all articles as bubbles and all links as lines."),
    html.Br(),
    dcc.Input(id='topic', type='text', value='Python (programming language)',\
              placeholder="topic"),
    dcc.Input(id='depth', type='number', value=2,\
              placeholder="search depth"),
    html.Button(id='submit-button-state', n_clicks=0, children='Start'),
    html.Br(),
    html.Br(),
    dcc.Markdown(id='current_state'),
    html.Br(),

    dcc.Dropdown(
        id='layout_dropdown',
        options=[
            {'label': 'Kamada Kawai Layout', 'value': 'kamada_kawai_layout'},
            {'label': 'Spring Layout', 'value': 'spring_layout'}
        ],
        value='kamada_kawai_layout'
    ),

    dcc.Markdown(id='dropdown_entry'),

    dcc.Graph(
        id='knowledge-graph',
        figure=fig
    )
])



#===============================================================================
# Callbacks - Interaktion mit der Benutzeroberfläche

# Mit @ wird ein sogenannter "Decorater" benutzt.
# Der Decorator führt dazu, dass die Funktion, die darunter deklariert wird
# (hier update_output) die Funktionalität des Decorators erhält.
# Hier werden Input, Output, State vom Paket dash.dependencies verwendet (siehe import).
# Wichtig ist, dass Inputs und Outputs mit den Argumenten und Returns der Funktion zusammenpassen!


@app.callback(Output('current_state', 'children'),
              Input('submit-button-state', 'n_clicks'),
              State('topic', 'value'),
              State('depth', 'value'))

def sanity_check(n_clicks, topic, depth):
    global graph
    graph = kn.KnowledgeGraph(topic, depth)

    if graph.topic:
        output = '''
            The current topic is **{}**
            and the depth of the network is **{}**.
        '''.format(topic, depth)

    else:
        output = "Topic does not exist."

    return output


@app.callback(Output('knowledge-graph', 'figure'),
              Input('current_state', 'children'),
              State('knowledge-graph', 'figure'),
              State('layout_dropdown', 'value'))

def update_figure(text, figure, layout):
    global graph
    if text == 'Topic does not exist.':
        figure['data'] = None
    else:
        graph.build()
        figure['data'] = graph.display(layout)

    return figure



@app.callback(Output('dropdown_entry', 'children'),
              Input('layout_dropdown', 'value'),
              prevent_initial_callbacks=True
)

def update_xyz(layout):
    return layout


#===============================================================================
# Server starten

if __name__ == '__main__':
    app.run_server(debug=True, port = 8000)
