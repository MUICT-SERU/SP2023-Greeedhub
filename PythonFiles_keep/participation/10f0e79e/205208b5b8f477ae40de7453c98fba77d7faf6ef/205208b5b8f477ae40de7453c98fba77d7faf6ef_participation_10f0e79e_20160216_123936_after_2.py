from .general import AAConfig
import percolation as P
from percolation.rdf import po

class MongoPublishing(AAConfig):
    translation_graph="participation_aamongo_translation"
    meta_graph="participation_aammongo_meta"
    snapshotid="aa-mongo-legacy"
    def __init__(self,mongoshouts):
        snapshotid=P.rdf.ic(po.AASnapshot,self.snapshotid,self.meta_graph)
        locals_=locals().copy(); del locals_["self"]
        participantvars=["nick","email"]
        messagevars=["textMessage","session","author","isValid","createdAt"]
        for i in locals_:
            exec("self.{}={}".format(i,i))
        self.rdfMongo()
    def rdfMongo(self):
        triples=[]
        for shout in self.mongoshouts:
            if not shout["nick"]:
                continue
            shouturi=P.rdf.ic(po.Shout,self.snapshotid+"-"+str(shout["_id"]),self.translation_graph,self.snapshoturi)
            triples+=[
                     (shouturi,po.provenance,"mongodb"),
                     (shouturi,po.textMessage,shout["shout"]),
                     (shouturi,po.createdAt,shout["time"]),
                     (shouturi,po.nick,shout["nick"]),
                     ]
        P.add(triples,self.translation_graph)
