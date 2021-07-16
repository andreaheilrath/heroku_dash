import wikipediaapi as wpa

import requests
import urllib.request as ur
from bs4 import BeautifulSoup

import xml.etree.ElementTree as ET

import time

#===============================================================================

wiki = wpa.Wikipedia('en')


#===============================================================================

def get_links(slug, base_url = 'http://141.23.210.106:8181/7fe4cca9-607f-5932-c685-9a22c1c410b5/A/'):

    start = time.time()

    page = requests.get(base_url + slug)

    mid = time.time()

    soup = BeautifulSoup(page.content, features = 'lxml')
    article = soup.h1.string

    #elements = soup.find('div', class_='mw-parser-output').find_all(['p', 'h2'])
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

    end = time.time()

    print('request duration', mid-start, 'other', end-mid)

    return link_dict

def valid_article(article):
    page = requests.get("https://en.wikipedia.org/w/index.php?search=" + article)
    url = str(page.url)
    slug = url[url.rfind('/')+1:]
    print(slug)
    soup = BeautifulSoup(page.content, features = 'lxml')
    page_title = soup.h1.string
    if article.lower() == page_title.lower():
        return page_title, slug

#===============================================================================

title, slug = valid_article('Linear Algebra')


print(get_links(slug))

#links = get_links(slug, base_url = "http://141.23.210.106:8181/7fe4cca9-607f-5932-c685-9a22c1c410b5/A/")
#print(links)
