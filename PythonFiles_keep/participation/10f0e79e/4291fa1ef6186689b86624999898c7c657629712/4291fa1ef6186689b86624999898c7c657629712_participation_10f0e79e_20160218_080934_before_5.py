from .general import AAConfig
import percolation as P
from percolation.rdf import po
class MysqlPublishing(AAConfig):
    translation_graph="participation_aamysql_translation"
    meta_graph="participation_aamysql_meta"
    snapshotid="aa-mysql-legacy"
    def __init__(self,mysqldict):
        # first aa implementation
        snapshotid=P.rdf.ic(po.AASnapshot,self.snapshotid,self.meta_graph)
        locals_=locals().copy(); del locals_["self"]
        participantvars=["nick","email"]
        messagevars=["textMessage","session","author","isValid","createdAt"]
        sessionvars=["screenshot","score","checker","checkMessage","createdAt"]
        comment="shouts from first AA, a fancy version of AA with sessions and screenshot urls"
        provenance="mysql"
        for i in locals_:
            exec("self.{}={}".format(i,i))
        self.rdfMysql()
    def rdfMysql(self):
        triples=[]
        user_dict={}
        for user in self.mysqldict["users"]:
            nick=user[2]
            if not nick:
                continue
            useruri=P.rdf.ic(po.Participant,nick,self.translation_graph,self.snapshoturi)
            user_dict[user[0]]=useruri
            triples+=[
                     (useruri,po.nick,nick)
                     ]
            email=user[1]
            if email:
                triples+=[
                         (useruri,po.email,nick)
                         ]

        for session in self.mysqldict["sessions"]:
            sessionuri=P.rdf.ic(po.Session,self.snapshotid+"-"+str(session[0]),self.translation_graph,self.snapshoturi)
            if session[1] not in user_dict:
                continue
            useruri=user_dict[session[1]]
            triples+=[
                     (sessionuri,po.participant,useruri),
                     (sessionuri,po.created,session[2]),
                     ]

            if session[3]:
                if session[3] in user_dict:
                    checker=user_dict[session[3]]
                    triples+=[
                             (sessionuri,po.checker,checker),
                             ]
            if session[4]:
                message=session[4]
                triples+=[
                         (sessionuri,po.checkMessage,message),
                         ]
            if session[5]:
                score=session[5]
                triples+=[
                         (sessionuri,po.checkScore,score),
                         ]
            if session[6]:
                sc=session[6]
                triples+=[
                         (sessionuri,po.screencast,sc),
                         ]
        for shout in self.mysqldict["messages"]:
            if shout[2] not in user_dict:
                continue
            shouturi=P.rdf.ic(po.Shout,self.snapshotid+"-"+str(shout[0]),self.translation_graph,self.snapshoturi)
            if int(shout[1]):
                sessionuri=po.Session+"#"+self.snapshotid+"-"+str(shout[1])
                triples+=[
                         (shouturi,po.session,sessionuri),
                         ]
            useruri=user_dict[shout[2]]
            triples+=[
                     (shouturi,po.author,useruri),
                     ]
            triples+=[
                     (shouturi,po.textMessage,shout[4]),
                     (shouturi,po.createdAt,shout[5]),
                     (shouturi,po.isValid,shout[6]),
                     ]
        P.add(triples,self.translation_graph)
