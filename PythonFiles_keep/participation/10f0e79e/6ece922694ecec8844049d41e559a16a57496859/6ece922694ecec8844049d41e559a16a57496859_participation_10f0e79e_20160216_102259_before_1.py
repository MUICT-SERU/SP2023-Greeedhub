from participation import DATADIR
import percolation as P, social as S, participation as Pa, rdflib as r, os
from percolation.rdf import NS, a, po, c
import MySQLdb, pymongo, codecs
exec(open(Pa.PARTICIPATIONDIR+"accesses.py").read())

def connectMysql():
    db2=MySQLdb.connect(user=aa.mysqluser1,passwd=aa.mysqlpassword1,db=aa.mysqldb1,use_unicode=True)
    db= MySQLdb.connect(user=aa.mysqluser2,passwd=aa.mysqlpassword2,db=aa.mysqldb2,use_unicode=True)

    db.query("SET NAMES utf8")
    db.query('SET character_set_connection=utf8')
    db.query('SET character_set_client=utf8')
    db.query('SET character_set_results=utf8')
    db2.query("SET NAMES utf8")
    db2.query('SET character_set_connection=utf8')
    db2.query('SET character_set_client=utf8')
    db2.query('SET character_set_results=utf8')

    db.query("show tables;")
    res=db.store_result()
    aa_tables=[res.fetch_row()[0][0] for i in range(res.num_rows())]
    d={}
    for tt in aa_tables:
        #db.query("select column_name from information_schema.columns where table_name='%s';"%(tt,))
        db.query("SHOW columns FROM %s;"%(tt,))
        res=db.store_result()
        d["h"+tt]=[res.fetch_row()[0][0] for i in range(res.num_rows())]
        db.query("select * from %s;"%(tt,))
        res=db.store_result()
        d[tt]=[res.fetch_row()[0] for i in range(res.num_rows())]
    db2.query("show tables;")
    res=db2.store_result()
    aa_tables=[res.fetch_row()[0][0] for i in range(res.num_rows())]
    d2={}
    for tt in aa_tables:
        db2.query("SHOW columns FROM %s;"%(tt,))
        res=db2.store_result()
        d2["h"+tt]=[res.fetch_row()[0][0] for i in range(res.num_rows())]
        db2.query("select * from %s;"%(tt,))
        res=db2.store_result()
        d2[tt]=[res.fetch_row()[0] for i in range(res.num_rows())]
    return d,d2

def connectMongo():
    client=pymongo.MongoClient(aa.mongouri)
    shouts=client.aaserver.shouts.find({})
    shouts_=[shout for shout in shouts]
    return shouts

def accessIrcLog():
    with codecs.open("../../social/data/irc/labmacambira_lalenia3.txt","rb","iso-8859-1")  as f:
        logtext=S.irc.log2rdf.textFix(f.read())
        logtext=P.utils.cleanText(logtext)
    return logtext
def accessOreShouts():
    g=r.Graph()
    for oredir in aa.oredirs:
        files=os.listdir(os.path.expanduser(oredir))
        for file_ in files:
            if file_.endswith(".ttl"):
                g.parse(os.path.expanduser(oredir)+file_,format="turtle")
            else:
                g.parse(os.path.expanduser(oredir)+file_)
    return g

def parseLegacyFiles(mysqldbs=True,mongoshouts=True,irclog=True,oreshouts=True):
    """Parse legacy files with aa shouts and sessions"""
    # access mysql, access mongo, access irc log from social/
    c("starting aa access")
    if mysqldbs:
        mysqldbs=connectMysql(); c("mysql ok") # mysqldata1,mysqldata2
    if mongoshouts:
        mongoshouts=connectMongo(); c("mongo ok")
    if irclog:
        irclog=accessIrcLog(); c("irc ok")
    if oreshouts:
        oreshouts=accessOreShouts(); c("ore ok")
    return mysqldbs,mongoshouts,irclog,oreshouts
