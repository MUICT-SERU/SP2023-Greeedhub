import psycopg2, rdflib as r, sys,urllib
import re
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
    cur.execute('SELECT * FROM users')
    users = cur.fetchall()
    cur.execute('SELECT * FROM profiles')
    profiles = cur.fetchall()
    cur.execute('SELECT * FROM articles')
    articles = cur.fetchall()
    cur.execute('SELECT * FROM comments')
    comments = cur.fetchall()
    cur.execute('SELECT * FROM friendships')
    friendships= cur.fetchall()
    cur.execute('SELECT * FROM votes')
    votes= cur.fetchall()
    cur.execute('SELECT * FROM tags')
    tags= cur.fetchall()
    cur.execute('SELECT * FROM taggings')
    taggings= cur.fetchall()

    # nome das colunas nas tabelas
    cur.execute("select column_name from information_schema.columns where table_name='users';")
    UN=cur.fetchall()
    UN=[i[0] for i in UN[::-1]]
    cur.execute("select column_name from information_schema.columns where table_name='profiles';")
    PN=cur.fetchall()
    PN=[i[0] for i in PN[::-1]]
    cur.execute("select column_name from information_schema.columns where table_name='articles';")
    AN=cur.fetchall()
    AN=[i[0] for i in AN[::-1]]
    cur.execute("select column_name from information_schema.columns where table_name='comments';")
    CN=cur.fetchall()
    CN=[i[0] for i in CN[::-1]]
    cur.execute("select column_name from information_schema.columns where table_name='friendships';")
    FRN=cur.fetchall()
    FRN=[i[0] for i in FRN[::-1]]
    cur.execute("select column_name from information_schema.columns where table_name='votes';")
    VN=cur.fetchall()
    VN=[i[0] for i in VN[::-1]]
    cur.execute("select column_name from information_schema.columns where table_name='tags';")
    TN=cur.fetchall()
    TN=[i[0] for i in TN[::-1]]
    cur.execute("select column_name from information_schema.columns where table_name='taggings';")
    TTN=cur.fetchall()
    TTN=[i[0] for i in TTN[::-1]]



