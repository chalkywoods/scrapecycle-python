from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import text
from sqlalchemy.orm.exc import FlushError
from sqlalchemy.exc import IntegrityError

from database.declaratives import Base, Board, Post

class Table():
    def __init__(self, session, declarative):
        self.session = session
        self.declarative = declarative

    def get(self, **criteria):
        queries = []
        for key, value in criteria.items():
            if type(value) is int:
                queries.append('{}.{} == {}'.format(self.declarative.__classname__, key, value))
            else:
                queries.append('{}.{} == "{}"'.format(self.declarative.__classname__, key, value))
        query_string = ' AND '.join(queries)
        query = self.session.query(self.declarative).filter(text(query_string))
        return query.all()

    def commit(self):
        try:
            self.session.commit()
        except (FlushError, IntegrityError):
            self.session.rollback()
            return False
        return True

class Posts(Table):
    def __init__(self, database):
        Table.__init__(self, database, Post)

    def add(self, id, post_type, date, name, location, update_time, group_name):
        self.session.add(Post(id=id, post_type=post_type, date=date, name=name, 
                                  location=location, update_time=update_time, group_name=group_name))
        return self.commit()

    def addAll(self, posts):
        for post in posts:
            self.session.add(Post(id=post[0], post_type=post[1], date=post[2], name=post[3], 
                                  location=post[4], update_time=post[5], group_name=post[6]))
        return self.commit()

class Groups(Table):
    def __init__(self, database):
        Table.__init__(self, database, Board)

    def add(self, name, location, unique_name, update_time = 0):
        self.session.add(Board(name=name, location=location, unique_name=unique_name, update_time=update_time))
        return self.commit()

class Database():
    def __init__(self, database):
        self.database = database
        engine = create_engine('sqlite:///{}'.format(database))
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        self.session = DBSession()
        self.groups = Groups(self.session)
        self.posts = Posts(self.session)

    def saved_group(self, group_name):
        return False