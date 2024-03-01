from participation import DATADIR
import percolation as P, social as S, os
from percolation.rdf import NS, a, po, c
import MySQLdb, pymongo, codecs
def connectMysql():
    db2=MySQLdb.connect(user="root",passwd="foobar",db="fbdb",use_unicode=True)
    db= MySQLdb.connect(user="root",passwd="foobar",db="fbdb2",use_unicode=True)
    db.query("SET NAMES utf8")
    db.query('SET character_set_connection=utf8')
    db.query('SET character_set_client=utf8')
    db.query('SET character_set_results=utf8')
    db.query("show tables;")
    res=db.store_result()
    aa_tables=[res.fetch_row()[0][0] for i in range(res.num_rows())]
    d={}
    for tt in aa_tables:
        db.query("select column_name from information_schema.columns where table_name='%s';"%(tt,))
        res=db.store_result()
        d["h"+tt]=[res.fetch_row()[0][0] for i in range(res.num_rows())]
        db.query("select * from %s;"%(tt,))
        res=db.store_result()
        d[tt]=[res.fetch_row()[0] for i in range(res.num_rows())]
    d2={}
    for tt in aa_tables:
        db2.query("select column_name from information_schema.columns where table_name='%s';"%(tt,))
        res=db2.store_result()
        d2["h"+tt]=[res.fetch_row()[0][0] for i in range(res.num_rows())]
        db2.query("select * from %s;"%(tt,))
        res=db2.store_result()
        d2[tt]=[res.fetch_row()[0] for i in range(res.num_rows())]
    return d,d2

def connectMongo():
    client=pymongo.MongoClient("mongodb://labmacambira:macambira00@ds031948.mongolab.com:31948/aaserver")
    shouts=client.aaserver.shouts.find({})
    shouts_=[shout for shout in shouts]
    return shouts

def parseIrcLog():
    with codecs.open("../../social/data/irc/labmacambira_lalenia3.txt","rb","iso-8859-1")  as f:
        logtext=S.irc.log2rdf.textFix(f.read())
    return logtext
def parseLegacyFiles(data_dir=DATADIR+"aa/"):
    """Parse legacy files with aa shouts and sessions"""
    # access mysql, access mongo, access irc log from social/
    mysqldata1,mysqldata2=connectMysql()
    mongoshouts=connectMongo()
    ircshouts=parseIrcLog()
    filenames=[]
    triples=[]
    snapshots=set()
    for filename in filenames:
        snapshotid="irc-legacy-"+filename.replace("#","")
        snapshoturi=po.TwitterSnapshot+"#"+snapshotid
        expressed_classes=[po.Participant,po.IRCMessage]
        expressed_reference=filename.replace("#","").replace(".txt","").replace(".log","")
        name_humanized="IRC log of channel "+expressed_reference
        filesize=os.path.getsize(data_dir+filename)/10**6
        fileformat="txt"
        fileuri=po.File+"#Irc-log-"+filename.replace("#","")
        triples+=[
                 (snapshoturi,a,po.Snapshot),
                 (snapshoturi,a,po.IRCSnapshot),
                 (snapshoturi,po.snapshotID,snapshotid),
                 (snapshoturi, po.isEgo, False),
                 (snapshoturi, po.isGroup, True),
                 (snapshoturi, po.isFriendship, False),
                 (snapshoturi, po.isInteraction, False),
                 (snapshoturi, po.isPost, True),
                 (snapshoturi, po.humanizedName, name_humanized),
                 (snapshoturi, po.expressedReference, expressed_reference),
                 (snapshoturi, po.rawFile, fileuri),
                 (fileuri,     po.fileSize, filesize),
                 (fileuri,     po.fileName, filename),
                 (fileuri,     po.fileFormat, fileformat),
                 ]+[
                 (fileuri,    po.expressedClass, expressed_class) for expressed_class in expressed_classes
                 ]
        snapshots.add(snapshoturi)
    nfiles=len(filenames)
    nsnapshots=3
    P.context("participation_aa","remove")
    platformuri=P.rdf.ic(po.Platform,"AA",context="participation_aa")
    triples+=[
             (NS.participation.Session,NS.social.nAASnapshots,nsnapshots),
             (platformuri, po.dataDir,data_dir),
             ]
    P.add(triples,context="participation_aa")
    c("parsed {} aa shout sources ({} snapshots) are in percolation graph and 'participation_aa' context".format(nfiles,nsnapshots))
    c("percolation graph have {} triples ({} in participation_aa context)".format(len(P.percolation_graph),len(P.context("participation_aa"))))
    negos=P.query(r" SELECT (COUNT(?s) as ?cs) WHERE         { GRAPH <participation_aa> { ?s po:isEgo true         } } ")
    ngroups=P.query(r" SELECT (COUNT(?s) as ?cs) WHERE       { GRAPH <participation_aa> { ?s po:isGroup true       } } ")
    nfriendships=P.query(r" SELECT (COUNT(?s) as ?cs) WHERE  { GRAPH <participation_aa> { ?s po:isFriendship true  } } ")
    ninteractions=P.query(r" SELECT (COUNT(?s) as ?cs) WHERE { GRAPH <participation_aa> { ?s po:isInteraction true } } ")
    nposts=P.query(r" SELECT (COUNT(?s) as ?cs) WHERE        { GRAPH <participation_aa> { ?s po:isPost true        } } ")
    totalsize=sum(P.query(r" SELECT ?size WHERE              { GRAPH <participation_aa> { ?s po:fileSize ?size     } } "))
    c("""{} are ego snapshots, {} are group snapshots
{} have a friendship structures. {} have an interaction structures. {} have texts 
Total raw data size is {:.2f}MB""".format(negos,ngroups,nfriendships,ninteractions,nposts,totalsize))
    return snapshots


