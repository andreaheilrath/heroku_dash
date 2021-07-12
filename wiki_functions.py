import wikipediaapi as wpa
import networkx as nx
import random

wiki = wpa.Wikipedia('en')

graph = nx.Graph()


query = 'mushrooms'
start_page = wiki.page(query)
graph.add_node(query)

if not start_page.exists():
    print("Error - page doesn't exist!\nPlease enter a valid page.")

for key in start_page.links:
    page = wiki.page(key)
    #print(page.title)
    graph.add_node(page.title)
    graph.add_edge(query, page.title)

#print(page.summary[:420])
'''
link_list = [key for key in page.links]

random_link = random.choice(link_list)

linked_page = wiki.page(random_link)

print(linked_page.exists())

print(linked_page.title)
'''
print(graph.nodes)

#print(linked_page.summary[:420])
