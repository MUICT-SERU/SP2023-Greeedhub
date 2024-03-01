import psycopg2, rdflib as r, sys,urllib
import re, participation as Pa
from percolation.rdf import NS, a, po, c
from .postgre2rdf import ParticipabrPublishing
exec(open(Pa.PARTICIPATIONDIR+"accesses.py").read())
TAG_RE = re.compile(r'<[^>]+>')
def remove_tags(text):
    return TAG_RE.sub('', text)


def parseLegacyFiles(mysqldb=True,mongoshouts=True,irclog=True,oreshouts=True):
    """Parse legacy files with aa shouts and sessions"""
    # access mysql, access mongo, access irc log from social/
    c("starting aa access")
    con = psycopg2.connect(database=participabr.postgre_database, user=participabr.postgre_user)
    cur = con.cursor()

    # dados das tabelas
    return ParticipabrPublishing(cur)


