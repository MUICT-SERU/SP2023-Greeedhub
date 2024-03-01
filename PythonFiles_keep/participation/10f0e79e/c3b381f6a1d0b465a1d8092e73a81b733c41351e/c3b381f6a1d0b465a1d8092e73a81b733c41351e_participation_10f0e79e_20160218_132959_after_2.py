import percolation as P, re, datetime
from .general import AAPublishing
from percolation.rdf import NS, po, a, c
class LogPublishing(AAPublishing):
    translation_graph="participation_aairc_translation"
    meta_graph="participation_aairc_meta"
    snapshotid="aa-irc-legacy"
    def __init__(self,logtext,final_path="aa_snapshots/"):
        AAPublishing.__init__(self,final_path,self.snapshotid)
        snapshoturi=P.rdf.ic(po.AASnapshot,self.snapshotid,self.meta_graph)
        #rmsg=r"(\d{4})\-(\d{2})\-(\d{2})T(\d{2}):(\d{2}):(\d{2})  \<(.*?)\> (.*)" # message
        rmsg=r"(\d{4})\-(\d{2})\-(\d{2})T(\d{2}):(\d{2}):(\d{2})  \<(.*?)\> (;aa +(.*)|lalenia[,:]{0,1} +aa +(.*))"
        participantvars=["nick"]
        messagevars=["textMessage","author","createdAt"]
        provenance="irc"
        comment="shouts from irc (input bu users through bots). Have many unique shouts, but also overlap with other AA snapshots and is contained by the labmacambira irc log rdf expression"
        locals_=locals().copy(); del locals_["self"]
        for i in locals_:
            exec("self.{}={}".format(i,i))
        self.rdfTranslate()
        self.makeMetadata()
        self.writeAll()
    def rdfTranslate(self):
        self.messages=re.findall(self.rmsg,self.logtext)
        #foo=re.findall(r"(\d{4})\-(\d{2})\-(\d{2})T(\d{2}):(\d{2}):(\d{2})  \<(.*?)\> (\;aa |lalenia[,:]{0,1} +aa) +(.*)",aa.logtext)
        #foo=re.findall(r"(\d{4})\-(\d{2})\-(\d{2})T(\d{2}):(\d{2}):(\d{2})  \<(.*?)\> (;aa +.*|lalenia[,:]{0,1} +aa +.*)",aa.logtext)
        # depende de como for a formatação, a ultima ou penultima msg: (a outra é nula)
        triples=[]
        c("found", len(self.messages), "aa shouts")
        for message in self.messages:
            year, month, day, hour, minute, second, nick, text, shout1, shout2=message
            datetime_=datetime.datetime(*[int(i) for i in (year,month,day,hour,minute,second)])
            shoutid=self.snapshotid+"-"+nick+"-"+datetime_.isoformat()
            shouturi=P.rdf.ic(po.Shout,shoutid,self.translation_graph,self.snapshoturi)
            if shout1:
                triples+=self.addText(shouturi,shout1)
            elif shout2:
                if shout2.startswith("shout"):
                    shout2=shout2[5:].strip()
                triples+=self.addText(shouturi,shout2)
            else:
                raise ValueError("Shout vazio?")
            participantid=self.snapshotid+"-"+nick
            participanturi=P.rdf.ic(po.Participant,participantid,self.translation_graph,self.snapshoturi)
            triples+=[
                     (shouturi, po.textMessage, text),
                     (shouturi, po.createdAt, datetime_),
                     (shouturi, po.author, participanturi),
                     (participanturi,po.nick,nick),
                     ]
        P.add(triples,self.translation_graph)
        self.writeTranslates("full")
