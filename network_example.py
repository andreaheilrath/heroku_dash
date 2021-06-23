# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import plotly.graph_objects as go
import networkx as nx


#===============================================================================
# Funktion um ein zufälliges Netzwerk zu erzeugen und zu plotten

def generate_network(n):
    '''
    Generates a random geometric graph with n nodes. Analyzes the edges and
    nodes, so that corresponding graphs can be generated. The function returns
    the graphs.
    '''
    G = nx.random_geometric_graph(n, 0.2)   # erzeugt einen zufälligen Graphen mit n Knoten

    edge_x = []
    edge_y = []
    for edge in G.edges():                  # hier werden Kanten aus dem Graph extrahiert
        x0, y0 = G.nodes[edge[0]]['pos']
        x1, y1 = G.nodes[edge[1]]['pos']
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)

    edge_trace = go.Scatter(        # erzeugt den Plot der die Kanten darstellt
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines')

    node_x = []
    node_y = []
    for node in G.nodes():          # hier werden Knoten aus dem Graph extrahiert
        x, y = G.nodes[node]['pos']
        node_x.append(x)
        node_y.append(y)

    node_trace = go.Scatter(         # erzeugt den Plot der die Knoten darstellt
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        marker=dict(                # bestimmt nur das aussehen der Knoten
            showscale=True,
            colorscale='YlGnBu',
            reversescale=True,
            size=10,
            colorbar=dict(
                thickness=15,
                title='Node Connections',
                xanchor='left',
                titleside='right'
            ),
            line_width=2))

    # in diesem Teil wird bestimmt, wie viele Verbindungen jeder Knoten hat
    # das ist in den G.adjaceny() gespreichert
    node_adjacencies = []
    node_text = []
    for node, adjacencies in enumerate(G.adjacency()):
        node_adjacencies.append(len(adjacencies[1]))
        node_text.append('# of connections: '+str(len(adjacencies[1])))

    # die Farbe der Knoten wird auf die Anzahl an Verbindungen gesetzt
    node_trace.marker.color = node_adjacencies

    # der Text der bei Hover angezeigt wird ist der node_text
    node_trace.text = node_text

    return [edge_trace, node_trace] #ausgegeben werden die beiden Plots / Traces


#===============================================================================
# Layout der App

# das Stylesheet ändert primär Schriftarten
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server


# Erzeuge den Anfangsplot - hier wird n auf 64 gesetzt
fig = go.Figure(data=generate_network(64),  # hier wird die Funktion von oben benutzt
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
    dcc.Input(id='topic', type='text', value='None'),
    dcc.Input(id='depth', type='number', value=64),
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
    fig = go.Figure(data=generate_network(depth),
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
