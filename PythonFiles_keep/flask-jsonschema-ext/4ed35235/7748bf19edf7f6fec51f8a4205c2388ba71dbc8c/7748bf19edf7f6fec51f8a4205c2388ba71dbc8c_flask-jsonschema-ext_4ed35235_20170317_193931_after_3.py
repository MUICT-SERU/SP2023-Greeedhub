from sqlalchemy import Column, Table, Integer, String, create_engine
from sqlalchemy import ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()
Session = sessionmaker()


class Post(Base):
    __tablename__ = 'post'
    __table_args__ = {'sqlite_autoincrement': True}
    post_id = Column(Integer, primary_key=True)
    post_value = Column(String)
    author_id = Column(Integer, ForeignKey('author.author_id'))


class Author(Base):
    __tablename__ = 'author'
    __table_args__ = {'sqlite_autoincrement': True}
    author_id = Column(Integer, primary_key=True)
    author_name = Column(String)

    posts = relationship(Post, backref='author')
