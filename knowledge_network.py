import wikipediaapi as wpa

import requests
import urllib.request as ur
from bs4 import BeautifulSoup

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

        url = self.wiki.page(self.topic).fullurl
        last_slash = url.rfind('/')
        slug = '/wiki' + url[last_slash:]


        self.nodes[self.topic]['slug'] = slug

        def add_links(origin, depth):

            links = get_links(self.nodes[origin]['slug'])

            for topic in links:
                if topic not in self:
                    self.add_node(topic)
                    self.nodes[topic]['slug'] = links[topic]
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

        def get_links(slug, base_url = 'https://en.wikipedia.org/'):

            page = requests.get(base_url + slug)

            soup = BeautifulSoup(page.content, features = 'lxml')
            article = soup.h1.string

            elements = soup.find_all(['p', 'h2'])
            links = []

            for e in elements:
                if e.name == 'h2': break
                links.extend(e.find_all('a'))

            link_dict = {}

            for link in links:
                try:
                    link_dict[link['title']] = link['href']
                except KeyError:
                    pass

            return link_dict

        add_links(self.topic, self.depth)

def display(self):

        pos = nx.spring_layout(self)
        centrality = nx.degree_centrality(self)

        node_x, node_y, marker_size, node_text = [], [], [], []

        for node in self.nodes():          # hier werden Knoten aus dem Graph extrahiert
            self.nodes[node]['pos'] = pos[node]
            self.nodes[node]['centrality'] = centrality[node]
            node_x.append(pos[node][0])
            node_y.append(pos[node][1])
            marker_size.append(pow(centrality[node], 0.5)*100)
            node_text.append(node)

        node_trace = go.Scatter(         # erzeugt den Plot der die Knoten darstellt
            x=node_x, y=node_y,
            mode='markers',
            hoverinfo='text',
            marker=dict(                # bestimmt nur das aussehen der Knoten
                showscale=True,
                colorscale='YlGnBu',
                reversescale=True,
                size=marker_size,
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
