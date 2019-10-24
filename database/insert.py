from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from declaratives import Base, Board, Post

engine = create_engine('sqlite:///freecycle.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# Insert an Address in the address table
new_board = Board(name='Sheffield City', location='Yorkshire and the Humber, United Kingdom', unique_name='SheffieldUK', update_time=0)
session.add(new_board)
session.commit()

new_post = Post(id=1, post_type='offer', date=0, name='A test post', location='here', update_time = 0, group_name='SheffieldUK')
session.add(new_post)
session.commit()