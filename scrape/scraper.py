import re
import math
import time
import datetime
import urllib.request as request
import urllib.parse as parse
from bs4 import BeautifulSoup

class Scraper():
    def __init__(self, database):
        self.base = 'https://www.freecycle.org'
        self.db = database

    def update_group(self, group_name, values = {}, post_type = 'all'):
        values['page'] = 1
        values['resultsperpage'] = 10
        soup = self.group_soup(group_name, values, post_type)
        if len(soup.body.find_all(text='There were no matching messages')) > 0:
            return
        main = soup.find(string=re.compile('Showing'))
        num_results = int(str(main).split()[5])
        values['resultsperpage'] = 100
        posts = []
        souptime = 0
        addtime = 0
        for page in range(math.ceil(num_results/100)):
            timer = time.time()
            soup = self.group_soup(group_name, values, post_type)
            values['page'] += 1
            soup_posts = soup.find_all(attrs={'class': re.compile('candy')})
            souptime += time.time() - timer
            timer = time.time()
            if not self.add_posts(soup_posts, group_name):
                break
            addtime += time.time() - timer
        print('Requested in {}s'.format(souptime))
        print('All persisted in {}s'.format(addtime))

    def group_soup(self, group_name, values, post_type = 'all'):
        full_url = self.group_url(group_name, values, post_type)
        print(full_url)
        page = request.urlopen(full_url)
        soup = BeautifulSoup(page, 'html.parser')
        return soup

    def new_group(self, search_term):
        url = 'https://www.freecycle.org/search'
        data = parse.urlencode(dict(keywords=search_term)).encode()
        req =  request.Request(url, data=data)
        page = request.urlopen(req)
        soup = BeautifulSoup(page, 'html.parser')
        try:
            group_list = [element.contents[0] for element in soup.find_all(attrs={'class': re.compile('bulleted')})[0].find_all('li')]
        except:
            group_list = []
        new_groups = self.group_from_search(group_list)
        return new_groups

    def group_from_search(self, group_list):
        groups = []
        for soup in group_list:
            unique_name = soup['href'].split('/')[-1]
            full_name = soup.contents[0].split('(')
            name = full_name[0].replace(' ', '')
            location = full_name[1].replace(')', '')
            self.db.groups.add(name, location, unique_name)
            groups.append(self.db.groups.get(unique_name=unique_name)[0])
        return groups

    def group_url(self, group_name, values, post_type):
        url = '/'.join([self.base, 'group', group_name, 'posts', post_type])
        full_url = '?'.join([url, value_string(values)])
        return full_url

    def add_posts(self, posts, group_name):
        parsetime = 0
        addtime = 0
        oldIds = [oldPost.id for oldPost in self.db.posts.get(group_name=group_name)]
        newPosts = []
        for post in posts:
            timer = time.time()
            post_id = post.contents[1].contents[-1]
            for char in ' #()': post_id=post_id.replace(char,"")
            id = int(post_id)
            name = post.contents[3].contents[1].string
            location = post.contents[3].contents[2].string
            for char in '()': location=location.replace(char,"")
            textDate = post.contents[1].contents[4]
            date = int(datetime.datetime.strptime(textDate, ' %a %b %d %H:%M:%S %Y').timestamp())
            post_type = post.contents[1].contents[1].contents[1].contents[1].lower().replace(' ','')
            parsetime += time.time() - timer
            if not id in oldIds:
                newPosts.append([id, post_type, date, name, location, int(time.time()), group_name])
        timer = time.time()
        if len(newPosts) == 0:
            return False
        else:
            success = self.db.posts.addAll(newPosts)
            return success

    def update_post(self, post):
        print('Scraper.update_post not implemented')
        return True

def value_string(values):
    return '&'.join(['{}={}'.format(key, value) for key, value in values.items()])
    
