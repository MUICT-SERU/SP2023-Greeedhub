import re
import psycopg2
import participation as Pa
from percolation.rdf import c
from .postgre2rdf import ParticipabrPublishing
exec(open(Pa.PARTICIPATIONDIR+"accesses.py").read())
TAG_RE = re.compile(r'<[^>]+>')


def remove_tags(text):
    return TAG_RE.sub('', text)


def parseLegacyFiles(mysqldb=True, mongoshouts=True,
                     irclog=True, oreshouts=True):
    """Parse legacy files with aa shouts and sessions"""
    # access mysql, access mongo, access irc log from social/
    c("starting participabr access")
    con = psycopg2.connect(
        database=participabr.postgre_database, user=participabr.postgre_user)
    cur = con.cursor()

    # dados das tabelas
    return ParticipabrPublishing(cur)
