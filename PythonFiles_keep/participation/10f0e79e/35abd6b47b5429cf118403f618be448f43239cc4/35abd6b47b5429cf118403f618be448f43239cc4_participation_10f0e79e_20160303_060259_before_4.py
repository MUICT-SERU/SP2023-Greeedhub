from .general import AAPublishing
import percolation as P
from percolation.rdf import po

class MongoPublishing(AAPublishing):
    translation_graph="participation_aamongo_translation"
    meta_graph="participation_aammongo_meta"
    snapshotid="aa-mongo-legacy"
    def __init__(self,mongoshouts):
        # minimum aa, aa01
        snapshoturi=P.rdf.ic(po.AASnapshot,self.snapshotid,self.meta_graph)
        provenance="mongodb"
        comment="shouts from minimum aa, a simplified mongodb version of AA (aka aa01)"
        participantvars=["nick"]
        messagevars=["textMessage","author","createdAt","provenance"]
        locals_=locals().copy(); del locals_["self"]
        for i in locals_:
            exec("self.{}={}".format(i,i))
        self.rdfMongo()
    def rdfMongo(self):
        triples=[]
        for shout in self.mongoshouts:
            if not shout["nick"]:
                continue
            shouturi=P.rdf.ic(po.Shout,self.snapshotid+"-"+str(shout["_id"]),self.translation_graph,self.snapshoturi)
            participanturi=P.rdf.ic(po.Participant,self.snapshotid+"-"+str(shout["nick"]),self.translation_graph,self.snapshoturi)
            triples+=[
                     (shouturi,po.provenance,"mongodb"),
                     (shouturi,po.textMessage,shout["shout"]),
                     (shouturi,po.createdAt,shout["time"]),
                     (shouturi,po.author,participanturi),
                     (participanturi,po.nick,shout["nick"]),
                     ]
        P.add(triples,self.translation_graph)
