# -*- coding: utf-8 -*-
import sys

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import plotly.graph_objects as go
import knowledge_network as kn



#===============================================================================
# Layout der App

# das Stylesheet ändert primär Schriftarten
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

if not "-l" in sys.argv:
    server = app.server
else:
    print("Running in local mode.")



# Erzeuge den Anfangsplot - hier wird n auf 64 gesetzt
fig = go.Figure(data = None,  # hier wird die Funktion von oben benutzt
             layout=go.Layout(
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=40), # ab hier nur Styling
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                )

app.layout = html.Div([
    html.H1("Hello"),
    html.Div("Have fun with the progam!"),
    html.Br(),
    dcc.Input(id='topic', type='text', value='Linear algebra'),
    dcc.Input(id='depth', type='number', value=1),
    html.Button(id='submit-button-state', n_clicks=0, children='Start'),
    html.Div(id='output-state'),
    html.Br(),
    dcc.Graph(
        id='example-graph',
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

@app.callback(Output('output-state', 'children'),
              Input('submit-button-state', 'n_clicks'),
              State('topic', 'value'),
              State('depth', 'value'))

def update_output(n_clicks, input1, input2):


    '''
    displays the user inputs on the page
    '''
    return u'''
        The program was started {} times,\n
        the topic is "{}",
        and the depth is "{}"
    '''.format(n_clicks, input1, input2)


@app.callback(Output('example-graph', 'figure'),
              Input('submit-button-state', 'n_clicks'),
              State('topic', 'value'),
              State('depth', 'value'))

def update_figure(n_klicks, topic, depth):
    '''
    generates a random network and corresponding plots
    figure is updated with the new plots
    '''
    graph = kn.KnowledgeGraph(topic, depth)
    graph.build()
    fig = go.Figure(data= graph.display(),
                 layout=go.Layout(
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20,l=5,r=5,t=40),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )
    return fig


#===============================================================================
# Server starten

if __name__ == '__main__':
    app.run_server(debug=True)
