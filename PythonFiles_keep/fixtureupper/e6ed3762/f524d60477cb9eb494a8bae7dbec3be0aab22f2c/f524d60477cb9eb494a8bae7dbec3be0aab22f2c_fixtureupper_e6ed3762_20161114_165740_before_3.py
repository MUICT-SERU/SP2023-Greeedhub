from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relation, sessionmaker

_Base = declarative_base()

class Article(_Base):
    __tablename__ = 'article'

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    sub_title = Column(String(255))

    main_author_id = Column(Integer, ForeignKey('author.id'))
    author = relation('Author', backref='articles')


class Author(_Base):
    __tablename__ = 'author'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    alias = Column(String(255))
