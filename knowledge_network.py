import wikipediaapi as wpa
import networkx as nx
import plotly.graph_objects as go
import re
import random
import math


class KnowledgeGraph(nx.DiGraph):
    def __init__(self, topic, depth):
        super().__init__()
        self.topic = topic
        self.depth = depth
        self.wiki = wpa.Wikipedia('en')

        self.exclude_start = ['Category:', 'Template:', 'Help:', 'Talk:', 'Wikipedia', "." ]
        self.exclude_any = ['(disambiguation)']

        wiki_page = self.wiki.page(self.topic)
        if not wiki_page.exists():
            print("Error - page doesn't exist!\nPlease enter a valid page.")

    def build(self):
        self.add_node(self.topic)
        self.nodes[self.topic]['pos'] = [0,0]

        def add_links(origin, depth):
            linked_topics = self.wiki.page(origin).links
            for topic in linked_topics:
                if valid(topic):
                    if topic not in self:
                        self.add_node(topic)
                        phi = random.randrange(0,360)
                        self.nodes[topic]['pos'] = \
                        [self.nodes[origin]['pos'][0] + math.cos(phi)*pow(depth,2),\
                        self.nodes[origin]['pos'][1]  - math.sin(phi)*pow(depth,2)]
                    self.add_edge(origin, topic)

                    if depth > 1:
                        add_links(topic, depth-1)



        def valid(topic):
            for expression in self.exclude_start:
                if topic.find(expression) == 0:
                    return False
            for expression in self.exclude_any:
                if topic.find(expression) > 0:
                    return False
            return True


        add_links(self.topic, self.depth)

    def random_display(self):
        node_x = []
        node_y = []
        node_text = []

        for node in self.nodes():          # hier werden Knoten aus dem Graph extrahiert
            node_x.append(self.nodes[node]['pos'][0])
            node_y.append(self.nodes[node]['pos'][1])
            node_text.append(node)

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

        edge_x = []
        edge_y = []
        for edge in self.edges():                  # hier werden Kanten aus dem Graph extrahiert
            x0, y0 = self.nodes[edge[0]]['pos']
            x1, y1 = self.nodes[edge[1]]['pos']
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

        # in diesem Teil wird bestimmt, wie viele Verbindungen jeder Knoten hat
        # das ist in den G.adjaceny() gespreichert
        node_adjacencies = []

        for node, adjacencies in enumerate(self.adjacency()):
            node_adjacencies.append(len(adjacencies[1]))
            #node_text.append('# of connections: '+str(len(adjacencies[1])))

        # die Farbe der Knoten wird auf die Anzahl an Verbindungen gesetzt
        node_trace.marker.color = node_adjacencies

        # der Text der bei Hover angezeigt wird ist der node_text
        node_trace.text = node_text

        return [edge_trace, node_trace] #ausgegeben werden die beiden Plots / Traces
