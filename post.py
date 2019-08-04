class Post:

    def __init__(self, post):
        self.title = post.contents[3].contents[1].string
        self.location = post.contents[3].contents[2]
        self.url = post.a.attrs['href']
        post_id = post.contents[1].contents[-1]
        for char in ' #()': post_id=post_id.replace(char,"")
        self.id = int(post_id)

    def __eq__(self, other): 
        if not isinstance(other, Post):
            return NotImplemented
        return self.id == other.id

    def __hash__(self):
        return self.id