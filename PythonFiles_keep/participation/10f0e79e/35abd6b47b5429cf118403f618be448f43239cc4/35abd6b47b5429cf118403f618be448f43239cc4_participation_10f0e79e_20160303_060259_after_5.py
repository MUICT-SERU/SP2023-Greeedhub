from .general import AAPublishing
import percolation as P
from percolation.rdf import po, c


class MysqlPublishing(AAPublishing):
    translation_graph = "participation_aamysql_translation"
    meta_graph = "participation_aamysql_meta"
    snapshotid = "aa-mysql-legacy"

    def __init__(self, mysqldict):
        # first aa implementation
        c("before first add")
        snapshoturi = P.rdf.ic(po.AASnapshot, self.snapshotid,
                               self.translation_graph)
        c("after first add")
        locals_ = locals().copy()
        messagevars = ["textMessage", "session", "author", "isValid",
                       "createdAt"]
        sessionvars = ["screenshot", "score", "checker", "checkMessage",
                       "createdAt"]
        comment = "shouts from first AA, a fancy version of AA with sessions \
            and screenshot urls"
        provenance = "mysql"
        participantvars = ["nick", "email"]
        del locals_["self"]
        for i in locals_:
            exec("self.{}={}".format(i, i))
        self.rdfMysql()

    def rdfMysql(self):
        c("started triplification of aa mysql legacy")
        triples = []
        user_dict = {}
        for user in self.mysqldict["users"]:
            nick = user[2]
            if not nick:
                continue
            useruri = P.rdf.ic(po.Participant, nick, self.translation_graph,
                               self.snapshoturi)
            user_dict[user[0]] = useruri
            triples += [
                       (useruri, po.nick, nick)
                       ]
            email = user[1]
            if email:
                triples += [
                           (useruri, po.email, nick)
                           ]
        c("finished triplification of participants")
        P.add(triples, self.translation_graph)
        c("finished add of participants")
        triples = []
        count = 0
        for session in self.mysqldict["sessions"]:
            sessionuri = P.rdf.ic(po.Session,
                                  self.snapshotid+"-"+str(session[0]),
                                  self.translation_graph, self.snapshoturi)
            if session[1] not in user_dict:
                continue
            useruri = user_dict[session[1]]
            triples += [
                       (sessionuri, po.participant, useruri),
                       (sessionuri, po.created, session[2]),
                       ]
            if session[3]:
                if session[3] in user_dict:
                    checker = user_dict[session[3]]
                    triples += [
                               (sessionuri, po.checkParticipant, checker),
                               ]
            if session[4]:
                message = session[4]
                triples += [
                           (sessionuri, po.checkMessage, message),
                           ]
            if session[5]:
                score = session[5]
                triples += [
                           (sessionuri, po.checkScore, score),
                           ]
            if session[6]:
                sc = session[6]
                triples += [
                           (sessionuri, po.screencast, sc),
                           ]
            count += 1
            if count % 90 == 0:
                c("finished sessions:", count, "ntriples", len(triples))
                P.add(triples, self.translation_graph)
                triples = []
        c("finished triplification of sessions")
        if triples:
            P.add(triples, self.translation_graph)
            c("finished add of sessions")
        triples = []
        count = 0
        for shout in self.mysqldict["messages"]:
            if shout[2] not in user_dict:
                continue
            shouturi = P.rdf.ic(po.Shout, self.snapshotid+"-"+str(shout[0]),
                                self.translation_graph, self.snapshoturi)
            if int(shout[1]):
                sessionuri = po.Session+"#"+self.snapshotid+"-"+str(shout[1])
                triples += [
                           (shouturi, po.session, sessionuri),
                           ]
            useruri = user_dict[shout[2]]
            triples += [
                       (shouturi, po.author, useruri),
                       ]
            triples += [
                       (shouturi, po.textMessage, shout[4]),
                       (shouturi, po.createdAt, shout[5]),
                       (shouturi, po.isValid, shout[6]),
                       ]
            count += 1
            if count % 70 == 0:
                c("finished shouts:", count, "ntriples", len(triples))
                P.add(triples, self.translation_graph)
                triples = []
        c("finished triplification of shouts")
        if triples:
            P.add(triples, self.translation_graph)
            c("finished add of shouts")
