import rdflib as r
from percolation.rdf import c
from participation.aa.mysql2rdf import MysqlPublishing
from participation.aa.mongo2rdf import MongoPublishing
from participation.aa.irc2rdf import LogPublishing
from participation.aa.ore import OrePublishing
import percolation as P
import os


def publishAll(mysqldb=None, mongoshouts=None, irclogs=None, oreshouts=None):
    """express aa shouts as RDF for publishing"""
    pub_dir='./aa_snapshots/'
    if not os.path.isdir(pub_dir):
        os.mkdir(pub_dir)
    if mysqldb:
        c("before mysql publishing")
        mysqldb = MysqlPublishing(mysqldb)
        g = P.context(mysqldb.translation_graph)
        g.serialize(pub_dir+"aamysql.ttl", "turtle")
        c("mysql ttl ok")
        g.serialize(pub_dir+"aamysql.rdf", "xml")
        c("mysql ok")
    if mongoshouts:
        mongoshouts = MongoPublishing(mongoshouts)
        g = P.context(mongoshouts.translation_graph)
        g.serialize(pub_dir+"aamongo.ttl", "turtle")
        c("mongo ttl ok")
        g.serialize(pub_dir+"aamongo.rdf", "xml")
        c("mongo ok")
    if irclogs:
        g = r.Graph()
        for irclog in irclogs:  # filenames
            irclog = LogPublishing(irclog)
            g += P.context(irclog.translation_graph)
        g.serialize(pub_dir+"aairc.ttl", "turtle")
        c("irc ttl ok")
        g.serialize(pub_dir+"aairc.rdf", "xml")
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
    ss = Pa.aa.access.parseLegacyFiles(1, 1, 1, 1)
    c("finished access, starting triplification")
    triplification_classes = Pa.aa.render.publishAll(*ss)
    c("finished publication of all aa")
