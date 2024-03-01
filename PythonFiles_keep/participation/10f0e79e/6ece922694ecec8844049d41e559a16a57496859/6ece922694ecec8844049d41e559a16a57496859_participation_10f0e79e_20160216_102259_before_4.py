import percolation as P
from percolation.rdf import NS, a, po, c
from .mysql2rdf import MysqlPublishing
from .mongo2rdf import MongoPublishing
from .irc2rdf import LogPublishing
from .ore import OrePublishing


def publishAll(mysqldbs=None,mongoshouts=None,irclog=None,oreshouts=None):
    """express aa shouts as RDF for publishing"""
    if mysqldbs:
        mysqlbds=MysqlPublishing(mysqldbs); c("mysql ok") # mysqldata1,mysqldata2
    if mongoshouts:
        mongoshouts=MongoPublishing(mongoshouts); c("mongo ok")
    if irclog:
        ircslog=LogPublishing(irclog); c("irc ok")
    if oreshouts:
        oreshouts=OrePublishing(oreshouts); c("ore ok")
    return mysqldbs,mongoshouts,irclog,oreshouts

def publishAny(snapshoturi):
    # publish to umbrelladir
    triples=[
            (snapshoturi,      po.dataDir, "?datadir"),
            (snapshoturi,      po.snapshotID, "?snapshotid"),
            (snapshoturi,      po.rawDirectory, "?directoryurifoo"),
            ("?directoryurifoo",    po.directoryName, "?directoryname"),
            ]
    data_dir,directory,snapshotid=P.get(triples)
    return MboxPublishing(snapshoturi,snapshotid,directory,data_dir)
