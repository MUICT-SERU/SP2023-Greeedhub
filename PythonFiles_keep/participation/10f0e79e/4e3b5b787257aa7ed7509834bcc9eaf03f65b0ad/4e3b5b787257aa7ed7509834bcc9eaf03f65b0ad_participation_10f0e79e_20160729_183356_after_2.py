from .general import AAPublishing
import datetime
import percolation as P
from percolation.rdf import po, c, a


class MongoPublishing(AAPublishing):
    translation_graph = "participation_aamongo_translation"
    meta_graph = "participation_aammongo_meta"
    snapshotid = "aa-mongo-legacy"
    provenance_prefix = 'aa-legacy'

    def __init__(self, mongoshouts):
        # minimum aa, aa01
        snapshoturi = P.rdf.ic(po.Snapshot, self.snapshotid,
                               self.meta_graph)
        provenance = "mongodb"
        comment = "shouts from minimum aa, a simplified mongodb version of \
            AA (aka aa01)"
        participantvars = ["nick"]
        messagevars = ["textMessage", "author", "createdAt", "provenance"]
        locals_ = locals().copy()
        del locals_["self"]
        for i in locals_:
            exec("self.{}={}".format(i, i))
        self.rdfMongo()
        self.makeMeta()

    def makeMeta(self):
        triples = [
                 (self.snapshoturi, a, po.Snapshot),
                 # (self.snapshoturi, a, po.AASnapshot),
                 # (self.snapshoturi, a, po.AAMongoSnapshot),
                 (self.snapshoturi, po.snapshotID, self.snapshotid),
                 (self.snapshoturi, po.isEgo, False),
                 (self.snapshoturi, po.isGroup, True),
                 (self.snapshoturi, po.isFriendship, False),
                 (self.snapshoturi, po.isInteraction, False),
                 (self.snapshoturi, po.isPost, True),
                 (self.snapshoturi, po.socialProtocol, 'Algorithmic Autoregulation'),
                 (self.snapshoturi, po.dateObtained, datetime.date(2016, 7, 11)),
                 ]
        P.add(triples, self.meta_graph)


    def rdfMongo(self):
        triples = []
        count = 0
        for shout in self.mongoshouts:
            if not shout["nick"]:
                continue
            shouturi = P.rdf.ic(po.Shout,
                                self.snapshotid+"-"+str(shout["_id"]),
                                self.translation_graph, self.snapshoturi)
            participanturi = P.rdf.ic(po.Participant,
                                      self.provenance_prefix+"-"+str(shout["nick"]),
                                      self.translation_graph, self.snapshoturi)
            obs = P.rdf.ic(po.Observation,
                                      self.snapshotid+"-"+str(shout["nick"]),
                                      self.translation_graph, self.snapshoturi)
            triples += [
                       (shouturi, po.provenance, "mongodb"),
                       (shouturi, po.text, shout["shout"]),
                       # (shouturi, po.nChars, len(shout["shout"])),
                       (shouturi, po.createdAt, shout["time"]),
                       (shouturi, po.author, participanturi),
                       (participanturi, po.observation, obs),
                       (obs, po.nick, shout["nick"]),
                       ]
            count += 1
            if count % 70 == 0:
                c("finished shouts:", count, "ntriples", len(triples))
                P.add(triples, self.translation_graph)
                triples = []
        if triples:
            P.add(triples, self.translation_graph)
        c("finished triplification of aa mongo legacy")
