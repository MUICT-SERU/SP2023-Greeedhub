import os
import MySQLdb
import pymongo
import rdflib as r
import participation as Pa
from percolation.rdf import c
exec(open(Pa.PARTICIPATIONDIR+"accesses.py").read())


def parseLegacyFiles(mysqldb=True, mongoshouts=True, irclog=True,
                     oreshouts=True):
    """Parse legacy files with aa shouts and sessions"""
    # access mysql, access mongo, access irc log from social/
    c("starting aa access")
    if mysqldb:
        mysqldb = connectMysql()
        c("mysql ok")
    if mongoshouts:
        mongoshouts = connectMongo()
        c("mongo ok")
    if irclog:
        irclogs = accessIrcLog()
        c("irc ok")
    if oreshouts:
        oreshouts = accessOreShouts()
        c("ore ok")
    return mysqldb, mongoshouts, irclogs, oreshouts


def connectMysql():
    db = MySQLdb.connect(user=aa.mysqluser2, passwd=aa.mysqlpassword2,
                         db=aa.mysqldb2, use_unicode=True)
    db.query("SET NAMES utf8")
    db.query('SET character_set_connection=utf8')
    db.query('SET character_set_client=utf8')
    db.query('SET character_set_results=utf8')
    db.query("show tables;")
    res = db.store_result()
    aa_tables = [res.fetch_row()[0][0] for i in range(res.num_rows())]
    d = {}
    for tt in aa_tables:
        # db.query("select column_name from information_schema.columns\
        #    where table_name='%s';"%(tt,))
        db.query("SHOW columns FROM %s;" % (tt,))
        res = db.store_result()
        d["h"+tt] = [res.fetch_row()[0][0] for i in range(res.num_rows())]
        db.query("select * from %s;" % (tt,))
        res = db.store_result()
        d[tt] = [res.fetch_row()[0] for i in range(res.num_rows())]
    return d


def connectMongo():
    client = pymongo.MongoClient(aa.mongouri)
    shouts = client.aaserver.shouts.find({})
    shouts_ = [shout for shout in shouts]
    return shouts_


def accessIrcLog():
    # logtext = ""
    # for logfile in aa.logfiles:
    #     with codecs.open(logfile, "rb", "iso-8859-1") as f:
    #         logtext_ = S.irc.log2rdf.textFix(f.read())
    #         logtext += "\n"+P.utils.cleanText(logtext_)
    return aa.logfiles[3:]


def accessOreShouts():
    g = r.Graph()
    for oredir in aa.oredirs:
        files = os.listdir(os.path.expanduser(oredir))
        for file_ in files:
            if file_.endswith(".ttl"):
                g.parse(os.path.expanduser(oredir)+file_, format="turtle")
            else:
                g.parse(os.path.expanduser(oredir)+file_)
    return g
