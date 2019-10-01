import os
import re
import math
import time
import json
import pickle
import urllib.request as request
import urllib.parse as parse
from bs4 import BeautifulSoup
from post import Post

def read_config(filename):
    config_file = open(filename, 'r')
    config = json.load(config_file)
    config_file.close()
    return config['group'], config['post_type'], config['search_terms']

def get_freecycle(group_name, values = {}, post_type = 'all'):
    base_url = 'https://groups.freecycle.org/group'
    value_string = '&'.join(['{}={}'.format(key, value) for key, value in values.items()])
    url = '/'.join([base_url, group_name, 'posts', post_type])
    full_url = '?'.join([url, value_string])
    print(full_url)
    page = request.urlopen(full_url)
    soup = BeautifulSoup(page, 'html.parser')
    return soup

def get_posts(group_name, values = {}, post_type = 'all'):
    values['page'] = 1
    values['resultsperpage'] = 10
    soup = get_freecycle(group_name, values, post_type)
    main = soup.find(string=re.compile('Showing'))
    num_results = int(str(main).split()[5])
    values['resultsperpage'] = 100
    posts = []
    for page in range(math.ceil(num_results/100)):
        soup = get_freecycle(group_name, values, post_type)
        values['page'] += 1
        soup_posts = soup.find_all(attrs={'class': re.compile('candy')})
        posts.extend([Post(post) for post in soup_posts])
    print(len(posts))
    return posts

def notify(title, location, post_url):
    base = 'https://maker.ifttt.com/trigger'
    event = 'freecycle_post'
    key = 'dYV0keKl289w4r9uHz1_6p'
    url = '/'.join([base, event, 'with/key', key])
    values = {'value1': parse.quote(title, safe=''), 'value2': parse.quote(location, safe=''), 'value3': parse.quote(post_url, safe='')}
    value_string = '&'.join(['{}={}'.format(key, value) for key, value in values.items()])
    full_url = '?'.join([url, value_string])
    request.urlopen(full_url)

def search_post(post, terms = []):
    found = False
    for term in terms:
        if str.lower(term) in str.lower(post.title):
            found = True
            break
    return found

def search_posts(posts, terms):
    return [post for post in posts if search_post(post, terms)]
    
def find_items(group_name, post_type, terms, values = {}):
    posts = get_posts(group_name = group_name, values = values, post_type = post_type)
    return search_posts(posts, terms)

with open('items.pkl', 'a+') as item_file:
    item_file.seek(0)
    loaded_items = pickle.load(item_file)
    all_items = loaded_items if type(loaded_items) is set else set([])
while True:
    group_name, post_type, terms = read_config('config.json')
    items = set(find_items(group_name, post_type, terms))
    new_items = items.difference(all_items)
    for item in new_items:
        notify(item.title, item.location, item.url)
    all_items.update(new_items)
    with open('items.pkl', 'w') as item_file:
        pickle.dump(all_items, item_file)
    time.sleep(600)
