import re
import math
import urllib.request as request
import urllib.parse as parse
from bs4 import BeautifulSoup
from post import Post

class Scraper():
    def __init__(self, database):
        self.base = 'https://www.freecycle.org'
        self.db = database

    def get_group(self, group_name, values = {}, post_type = 'all'):
        values['page'] = 1
        values['resultsperpage'] = 10
        soup = self.group_soup(group_name, values, post_type)
        main = soup.find(string=re.compile('Showing'))
        num_results = int(str(main).split()[5])
        values['resultsperpage'] = 100
        posts = []
        for page in range(math.ceil(num_results/100)):
            soup = self.group_soup(group_name, values, post_type)
            values['page'] += 1
            soup_posts = soup.find_all(attrs={'class': re.compile('candy')})
            if not self.add_posts(soup_posts, post_type, group_name):
                break
        return posts

    def group_soup(self, group_name, values, post_type = 'all'):
        full_url = self.group_url(group_name, values, post_type)
        print(full_url)
        page = request.urlopen(full_url)
        soup = BeautifulSoup(page, 'html.parser')
        return soup

    def group_url(self, group_name, values, post_type):
        url = '/'.join([self.base, 'group', group_name, 'posts', post_type])
        full_url = '?'.join([url, value_string(values)])
        return full_url

    def add_posts(self, posts, post_type, group_name):
        for post in posts:
            post_id = post.contents[1].contents[-1]
            for char in ' #()': post_id=post_id.replace(char,"")
            id = int(post_id)
            name = post.contents[3].contents[1].string
            location = 'here'
            date = 0
            if not self.db.posts.add(id, post_type, date, name, location, group_name):
                return False
        return True

def value_string(values):
    return '&'.join(['{}={}'.format(key, value) for key, value in values.items()])
    
