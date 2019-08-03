import os
import re
import math
import urllib.request as request
from bs4 import BeautifulSoup

def get_freecycle(group_name, values = {}, post_type = 'all'):
    base_url = 'https://groups.freecycle.org/group'
    value_string = '&'.join(['{}={}'.format(key, value) for key, value in values.items()])
    url = '/'.join([base_url, group_name, 'posts', post_type])
    full_url = '?'.join([url, value_string])
    print(full_url)
    page = request.urlopen(full_url)
    soup = BeautifulSoup(page, 'html.parser')
    return soup
    
def parse_post(post):
    post_info = {}
    post_info['title'] = post.contents[3].contents[1].string
    post_info['location'] = post.contents[3].contents[2]
    post_info['url'] = post.a.attrs['href']
    return post_info

def get_posts(group_name, values = {}, post_type = 'all'):
    soup = get_freecycle(group_name, values, post_type)
    main = soup.find(string=re.compile('Showing'))
    num_results = int(str(main).split()[5])
    values['resultsperpage'] = 100
    posts = []
    values['page'] = 1
    for page in range(math.ceil(num_results/100)):
        soup = get_freecycle(group_name, values, post_type)
        values['page'] += 1
        soup_posts = soup.find_all(attrs={'class': re.compile('candy')})
        posts.extend([parse_post(post) for post in soup_posts])
    print(len(posts))
    return posts

def search_post(post, terms = []):
    found = False
    for term in terms:
        if str.lower(term) in str.lower(post['title']):
            found = True
            break
    return found

def search_posts(posts, terms):
    return [post for post in posts if search_post(post, terms)]
    
def find_items(group_name, post_type, terms, values = {}):
    posts = get_posts(group_name = group_name, values = values, post_type = post_type)
    return search_posts(posts, terms)

group_name = 'SheffieldUK'
post_type = 'offer'
terms = ['chair']
items = find_items(group_name, post_type, terms)

print([item['title'] for item in items])

