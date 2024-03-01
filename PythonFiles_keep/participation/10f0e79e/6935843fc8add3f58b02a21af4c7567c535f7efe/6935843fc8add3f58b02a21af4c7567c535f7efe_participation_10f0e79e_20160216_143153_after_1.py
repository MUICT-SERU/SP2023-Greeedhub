import percolation as P, re
from percolation.rdf import NS, po, a, c
class LogPublishing:
    translation_graph="participation_aairc_translation"
    meta_graph="participation_aairc_meta"
    snapshotid="aa-irc-legacy"
    def __init__(self,logtext):
        snapshotid=P.rdf.ic(po.AASnapshot,self.snapshotid,self.meta_graph)
        rmsg=r"(\d{4})\-(\d{2})\-(\d{2})T(\d{2}):(\d{2}):(\d{2})  \<(.*?)\> (.*)" # message
        participantvars=["nick"]
        messagevars=["textMessage","author","createdAt"]
        provenance="irc"
        comment="shouts from irc (input bu users through bots). Have many unique shouts, but also overlap with other AA snapshots and is contained by the labmacambira irc log rdf expression"
        locals_=locals().copy(); del locals_["self"]
        for i in locals_:
            exec("self.{}={}".format(i,i))
        self.rdfLog()
    def rdfLog(self):
        self.messages=re.findall(self.rmsg,self.logtext)
        #foo=re.findall(r"(\d{4})\-(\d{2})\-(\d{2})T(\d{2}):(\d{2}):(\d{2})  \<(.*?)\> (\;aa |lalenia[,:]{0,1} +aa) +(.*)",aa.logtext)
        #foo=re.findall(r"(\d{4})\-(\d{2})\-(\d{2})T(\d{2}):(\d{2}):(\d{2})  \<(.*?)\> (;aa +.*|lalenia[,:]{0,1} +aa +.*)",aa.logtext)
        for message in messages:
            text=message[-1]
            if text.startswith(";aa ") or text.startswith("lalenia, aa ") or text.startswith("lalenia: aa ") or text.startswith("lalenia aa "):
