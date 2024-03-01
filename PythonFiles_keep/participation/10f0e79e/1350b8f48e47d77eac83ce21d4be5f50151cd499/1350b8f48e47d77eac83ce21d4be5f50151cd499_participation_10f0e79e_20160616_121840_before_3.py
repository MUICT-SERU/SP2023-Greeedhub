from percolation.rdf import c
from participation.aa.mysql2rdf import MysqlPublishing
from participation.aa.mongo2rdf import MongoPublishing
from participation.aa.irc2rdf import LogPublishing
from participation.aa.ore import OrePublishing


def publishAll(mysqldb=None, mongoshouts=None, irclogs=None, oreshouts=None):
    """express aa shouts as RDF for publishing"""
    if mysqldb:
        c("before mysql publishing")
        mysqldb = MysqlPublishing(mysqldb)
        c("mysql ok")
    if mongoshouts:
        mongoshouts = MongoPublishing(mongoshouts)
        c("mongo ok")
    if irclogs:
        for irclog in irclogs:  # filenames
            irclog = LogPublishing(irclog)
            c("irc ok")
    if oreshouts:
        oreshouts = OrePublishing(oreshouts)
        c("ore ok")
    return mysqldb, mongoshouts, irclog, oreshouts

if __name__ == "__main__":
    # ss=Pa.aa.access.parseLegacyFiles(1,0,0,0)
    # ss=Pa.aa.access.parseLegacyFiles(0,1,0,0)
    # ss=Pa.aa.access.parseLegacyFiles(0,0,1,0)
    import participation as Pa
    c("started access")
    # ss = Pa.aa.access.parseLegacyFiles(0, 0, 1, 0)
    ss = Pa.aa.access.parseLegacyFiles(1, 0, 1, 1)
    c("finished access, starting triplification")
    triplification_classes = Pa.aa.render.publishAll(*ss)
    c("finished publication of all aa")
