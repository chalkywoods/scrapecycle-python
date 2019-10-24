import time
from database.posts import Database
from scrape.scraper import Scraper

class ActivePosts():
    def __init__(self, database='freecycle.db', cache_time = 600):
        self.database = Database(database)
        self.scraper = Scraper(self.database)
        self.cache_time = cache_time

    def get_posts(self, group_name, post_type = 'offer'):
        group = self.database.groups.get(unique_name=group_name)
        print(group)
        if len(group) > 0:
            group = group[0]
        else:
            group = self.generate_group(group_name)
        if int(time.time()) - group.update_time > self.cache_time:
            self.scraper.update_group(group.unique_name)
            group = self.database.groups.get(unique_name=group.unique_name)[0]
        return [post for post in group.posts if post.post_type == post_type]
        
    def generate_group(self, name):
        groups = self.scraper.new_group(name)
        print('Found groups {}'.format([group.unique_name for group in groups]))
        return groups[0]

    def search_posts(self, name, terms, post_type='offer'):
        posts = self.get_posts(name, post_type)
        matches = [post for post in posts if search_post(post, terms)]
        current = []
        for post in matches:
            if int(time.time()) - post.update_time < self.cache_time:
                current.append(post)
            elif self.scraper.update_post(post):
                current.append(self.database.posts.get(id=post.id)[0])
        return current

    def parse_group(self, group_name, selector = lambda x : x[0]):
        group = self.database.saved_group(group_name)
        if not group:
            groups = self.scraper.new_group(group_name)
        if len(groups) == 0:
            return False
        else:
            group = selector(groups)
            return group

def search_post(post, terms = []):
    found = False
    for term in terms:
        if str.lower(term) in str.lower(post.name):
            found = True
            break
    return found

class Freecycle():
    def __init__(self, database='freecycle.db', cache_time = 600):
        self.posts = ActivePosts(database, cache_time)

    def search(self, search_terms, group_name, post_type = 'offer'):
        group = self.posts.parse_group(group_name)
        if not group:
            return []
        else:
            return self.posts.search_posts(group.unique_name, search_terms, post_type)
