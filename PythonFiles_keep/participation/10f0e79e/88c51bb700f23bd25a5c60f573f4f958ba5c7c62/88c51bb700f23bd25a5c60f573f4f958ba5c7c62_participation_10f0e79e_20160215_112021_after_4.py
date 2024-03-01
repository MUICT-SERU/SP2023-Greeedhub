from participation import DATADIR
import percolation as P, os
from percolation.rdf import NS, a, po, c
import _mysql

def parseLegacyFiles(data_dir=DATADIR+"aa/"):
    """Parse legacy files with aa shouts and sessions"""
    # access mysql, access mongo, access irc log from social/
    filenames=[]
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
                 (snapshoturi, po.isInteraction, True),
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
    nsnapshots=len(snapshots)
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


