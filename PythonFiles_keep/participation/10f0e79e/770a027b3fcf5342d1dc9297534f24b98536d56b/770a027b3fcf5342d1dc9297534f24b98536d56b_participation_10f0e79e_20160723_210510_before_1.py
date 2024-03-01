import re
import datetime
import codecs
import social as S
import percolation as P
from .general import AAPublishing
from percolation.rdf import po, c, a
regex_url = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|'
                       r'[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
rmsg = (r"(\d{4})\-(\d{2})\-(\d{2})T(\d{2}):(\d{2}):(\d{2})  \<(.*?)\>"
        r" (;aa +(.*)|lalenia[,:]{0,1} +aa +(.*))")


class LogPublishing(AAPublishing):
    meta_graph = "participation_aairc_meta"

    def __init__(self, logfile, final_path="aa_snapshots/"):
        # AAPublishing.__init__(self, final_path, self.snapshotid)
        snapshotid = "aa-irc-legacy-"+logfile.split("/")[-1].replace("#", "")
        translation_graph = "participation_aairc_translation-"+snapshotid
        snapshoturi = P.rdf.ic(po.AASnapshot, snapshotid,
                               translation_graph)
        # rmsg=r"(\d{4})\-(\d{2})\-(\d{2})T(\d{2}):(\d{2}):(\d{2}) \
        #    \<(.*?)\> (.*)" # message
        participantvars = ["nick"]
        messagevars = ["textMessage", "author", "createdAt"]
        provenance = "irc"
        comment = "shouts from irc (input by users through bots). Have many \
            unique shouts, but also overlap with other AA snapshots and is \
            contained by the labmacambira irc log rdf expression"
        locals_ = locals().copy()
        del locals_["self"]
        for i in locals_:
            exec("self.{}={}".format(i, i))
        self.rdfTranslate()
        self.makeMeta()
        # self.writeAll()

    def makeMeta(self):
        triples = [
                 (self.snapshoturi, a, po.Snapshot),
                 # (self.snapshoturi, a, po.AASnapshot),
                 # (self.snapshoturi, a, po.AAIRCSnapshot),
                 (self.snapshoturi, po.snapshotID, self.snapshotid),
                 (self.snapshoturi, po.isEgo, False),
                 (self.snapshoturi, po.isGroup, True),
                 (self.snapshoturi, po.isFriendship, False),
                 (self.snapshoturi, po.isInteraction, False),
                 (self.snapshoturi, po.isPost, True),
                 (self.snapshoturi, po.socialProtocol, 'Algorithmic Autoregulation'),
                 (self.snapshoturi, po.dateObtained, datetime.date(2015, 7, 15)),
                 ]
        P.add(triples, self.meta_graph)

    def rdfTranslate(self):
        with codecs.open(self.logfile, "rb", "iso-8859-1") as f:
            logtext = P.utils.cleanText(S.irc.log2rdf.textFix(f.read()))

        self.messages = re.findall(rmsg, logtext)
        # foo=re.findall(r"(\d{4})\-(\d{2})\-(\d{2})T(\d{2}):(\d{2}):(\d{2}) \
        #    \<(.*?)\> (\;aa |lalenia[,:]{0,1} +aa) +(.*)",aa.logtext)
        # foo=re.findall(r"(\d{4})\-(\d{2})\-(\d{2})T(\d{2}):(\d{2}):(\d{2}) \
        #     \<(.*?)\> (;aa +.*|lalenia[,:]{0,1} +aa +.*)",aa.logtext)
        # depende de como for a formatação, a ultima ou penultima msg:
        # (a outra é nula)
        triples = []
        c("found", len(self.messages), "aa shouts")
        count = 0
        for message in self.messages:
            year, month, day, hour, minute, second, \
                nick, text, shout1, shout2 = message
            datetime_ = datetime.datetime(*[int(i) for i in (year, month,
                                            day, hour, minute, second)])
            shoutid = self.snapshotid+"-"+nick+"-"+datetime_.isoformat()
            shouturi = P.rdf.ic(po.Shout, shoutid, self.translation_graph,
                                self.snapshoturi)
            if shout1:
                # triples += self.addText(shouturi, shout1)
                shout_text = shout1
            elif shout2:
                # if shout2.startswith("shout"):
                #     shout2 = shout2[5:].strip()
                shout_text = shout2[5:].strip()
                # triples += self.addText(shouturi, shout2)
            else:
                raise ValueError("Shout vazio?")
            triples += [
                      (shouturi, po.text, shout_text),
                      (shouturi, po.nChars, len(shout_text)),
                      ]
            urls = regex_url.findall(shout_text)
            for url in urls:
                triples += [
                           (shouturi, po.hasUrl, url),
                           ]
            participantid = self.snapshotid+"-"+nick
            participanturi = P.rdf.ic(po.Participant, participantid,
                                      self.translation_graph, self.snapshoturi)
            triples += [
                       (shouturi, po.textMessage, text),
                       (shouturi, po.createdAt, datetime_),
                       (shouturi, po.author, participanturi),
                       (participanturi, po.nick, nick),
                       ]
            count += 1
            if count % 70 == 0:
                c("finished shouts:", count, "ntriples", len(triples))
                P.add(triples, self.translation_graph)
                triples = []
        if triples:
            P.add(triples, self.translation_graph)
        c("finished irc log shouts from", self.snapshotid)
        # self.writeTranslates("full")
