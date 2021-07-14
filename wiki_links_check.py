import wikipediaapi as wpa

import requests
import urllib.request as ur
from bs4 import BeautifulSoup

import time

#===============================================================================

wiki = wpa.Wikipedia('en')


#===============================================================================

def get_links(slug, base_url = 'https://en.wikipedia.org/'):

    start = time.time()

    page = requests.get(base_url + slug)

    mid = time.time()

    soup = BeautifulSoup(page.content, features = 'lxml')
    article = soup.h1.string

    elements = soup.find('div', class_='mw-parser-output').find_all(['p', 'h2'])
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

    end = time.time()

    print('request duration', mid-start, 'other', end-mid)

    return link_dict

#===============================================================================


slug = 'wiki/Barack_Obama'
#slug = 'wiki/Linear_algebra'

links = get_links(slug)

#print(links)
