import requests
from bs4 import BeautifulSoup
import networkx as nx
import plotly.graph_objects as go


def build(topic, depth, slug, local, base_url):

    #print('\n======================================== \nBuilding new graph around', topic, 'depth', depth, '\n======================================== ')

    self = nx.DiGraph()

    self.add_node(topic)
    self.nodes[topic]['slug'] = slug

    def add_links(origin, depth):
        links = get_links(self.nodes[origin]['slug'])
        for topic in links:
            if topic not in self:
                #print(topic, links[topic])
                self.add_node(topic)
                self.nodes[topic]['slug'] = links[topic]
            self.add_edge(origin, topic)
            if depth > 1:
                add_links(topic, depth-1)


    def get_links(slug):

        def to_dict(links, shift=0):
            link_dict = {}
            for link in links:
                try:
                    link_dict[link['title']] = link['href'][shift:]
                except KeyError:
                    pass
            return link_dict

        page = requests.get(base_url + slug)
        soup = BeautifulSoup(page.content, features = 'lxml')
        article = soup.h1.string

        links = []
        elements = soup.find_all(['p', 'h2'])
        for e in elements:
            if e.name == 'h2': break
            links.extend(e.find_all('a'))

        if local:
            link_dict = to_dict(links)
        else:
            link_dict = to_dict(links, 6)

        return link_dict

    add_links(topic, depth)

    #print('\n======================================== \n Done! \n========================================')

    return nx.node_link_data(self)


def display(json_graph, layout):

    self = nx.node_link_graph(json_graph)

    layout_dict = {'kamada_kawai_layout': nx.kamada_kawai_layout,
                        'shell_layout' : nx.shell_layout,
                        'spring_layout': nx.spring_layout,
                        'spectral_layout': nx.spectral_layout,
                        'spiral_layout': nx.spiral_layout
                        }

    layout = layout_dict[layout]

    pos = layout(self)

    centrality = nx.degree_centrality(self)
    node_x, node_y, marker_size, node_text = [], [], [], []

    for node in self.nodes():          # hier werden Knoten aus dem Graph extrahiert
        node_x.append(pos[node][0])
        node_y.append(pos[node][1])
        marker_size.append(pow(centrality[node], 0.5)*100)
        node_text.append(str(node))

    node_adjacencies = []
    for node, adjacencies in enumerate(self.adjacency()):
        node_adjacencies.append(len(adjacencies[1]))


    node_trace = go.Scatter(         # erzeugt den Plot der die Knoten darstellt
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        text=node_text,
        marker=dict(showscale=True, colorscale='YlGnBu', reversescale=True,
                    size=marker_size,
                    color=node_adjacencies,
                    colorbar=dict(thickness=15, title='Node Connections',
                                  xanchor='left', titleside='right'),
                    line_width=2))

    edge_x, edge_y = [], []
    for edge in self.edges():
        edge_x.extend([pos[edge[0]][0], pos[edge[1]][0], None])
        edge_y.extend([pos[edge[0]][1], pos[edge[1]][1], None])

    edge_trace = go.Scatter(x=edge_x, y=edge_y,
                            line=dict(width=0.5, color='#888'),
                            hoverinfo='none')

    return [edge_trace, node_trace]


def valid_article(article):
    page = requests.get("https://en.wikipedia.org/w/index.php?search=" + article)
    url = str(page.url)
    slug = url[url.rfind('/')+1:]
    soup = BeautifulSoup(page.content, features = 'lxml')
    page_title = soup.h1.string
    if article.lower() == page_title.lower():
        return page_title, slug
    else:
        return None, None


'''
    def valid(topic):
        for expression in self.exclude_start:
            if topic.find(expression) == 0:
                return False
        for expression in self.exclude_any:
            if topic.find(expression) > 0:
                return False
        return True
'''
