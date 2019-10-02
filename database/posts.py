from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import text

from declaratives import Base, Board, Post

class Posts():

    def __init__(self, database):
        self.database = database
        engine = create_engine('sqlite:///{}'.format(database))
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        self.session = DBSession()

    def add(self, id, post_type, date, name, location, board_name):
        self.session.add(Post(id=id, post_type=post_type, date=date, name=name, 
                                  location=location, board_name=board_name))
        self.session.commit()

    def get(self, **criteria):
        queries = []
        for key, value in criteria.items():
            if type(value) is int:
                queries.append('Post.{} == {}'.format(key, value))
            else:
                queries.append('Post.{} == "{}"'.format(key, value))
        query_string = ' AND '.join(queries)
        query = self.session.query(Post).filter(text(query_string))
        return query.all()

    
