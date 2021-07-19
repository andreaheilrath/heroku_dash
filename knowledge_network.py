import requests
from bs4 import BeautifulSoup
import networkx as nx
import plotly.graph_objects as go


class KnowledgeGraph(nx.DiGraph):#http://192.168.178.41:8181
    def __init__(self, topic, depth, layout, base_url, local):
        super().__init__()
        self.topic = topic
        self.depth = depth
        self.layout = layout
        self.base_url = base_url
        self.local = local

        self.layout_dict = {'kamada_kawai_layout': nx.kamada_kawai_layout,
                            'shell_layout' : nx.shell_layout,
                            'spring_layout': nx.spring_layout,
                            'spectral_layout': nx.spectral_layout,
                            'spiral_layout': nx.spiral_layout
                            }

        self.exclude_start = ['Category:', 'Template:', 'Help:', 'Talk:', 'Wikipedia', "." ]
        self.exclude_any = ['(disambiguation)']

        def valid_article(article):
            page = requests.get("https://en.wikipedia.org/w/index.php?search=" + article)
            url = str(page.url)
            slug = url[url.rfind('/')+1:]
            if not self.local:
                slug = '/wiki/' + slug
            soup = BeautifulSoup(page.content, features = 'lxml')
            page_title = soup.h1.string
            if article.lower() == page_title.lower():
                return page_title, slug
            else:
                return None, None

        self.topic, self.slug = valid_article(self.topic)

    def build(self):

        self.add_node(self.topic)
        self.nodes[self.topic]['pos'] = [0,0]
        self.nodes[self.topic]['slug'] = self.slug

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

        def get_links(slug):#base_url = 'https://en.wikipedia.org/'):

            page = requests.get(self.base_url + slug)
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
                    link_dict[str(link['title'])] = link['href']
                    print(link['href'])
                except KeyError:
                    pass

            return link_dict

        add_links(self.topic, self.depth)

    def display(self):

        layout = self.layout_dict[self.layout]
        pos = layout(self)

        centrality = nx.degree_centrality(self)

        node_x, node_y, marker_size, node_text = [], [], [], []


        for node in self.nodes():          # hier werden Knoten aus dem Graph extrahiert
            self.nodes[node]['pos'] = pos[node]
            self.nodes[node]['centrality'] = centrality[node]
            node_x.append(pos[node][0])
            node_y.append(pos[node][1])
            marker_size.append(pow(centrality[node], 0.5)*100)
            node_text.append(str(node))

        node_trace = go.Scatter(         # erzeugt den Plot der die Knoten darstellt
            x=node_x, y=node_y,
            #x=[0,1], y=[0,1],
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
            #x=[0,1], y=[0,1],
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines')

        # in diesem Teil wird bestimmt, wie viele Verbindungen jeder Knoten hat
        # das ist in den G.adjaceny() gespreichert
        node_adjacencies = []

        for node, adjacencies in enumerate(self.adjacency()):
            node_adjacencies.append(len(adjacencies[1]))
            node_text.append('# of connections: '+str(len(adjacencies[1])))

        # die Farbe der Knoten wird auf die Anzahl an Verbindungen gesetzt
        node_trace.marker.color = node_adjacencies

        # der Text der bei Hover angezeigt wird ist der node_text
        node_trace.text = node_text

        return [edge_trace, node_trace] #ausgegeben werden die beiden Plots / Traces
