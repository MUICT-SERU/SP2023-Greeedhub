from percolation.rdf import NS, po, a, c
import percolation as P, numpy as n, nltk as k, os
class AAPublishing:
    hastext=True
    isinteraction=False
    isfriendship=False
    def __init__(self,final_path="some_snapshots"):
        final_path_="{}{}/".format(final_path,self.snapshotid)
        if not os.path.isdir(final_path):
            os.mkdir(final_path)
        if not os.path.isdir(final_path_):
            os.mkdir(final_path_)
        size_chars_overall=[]; size_tokens_overall=[]; size_sentences_overall=[]
        locals_=locals().copy(); del locals_["self"]
        for i in locals_:
            exec("self.{}={}".format(i,i))
    def makeMetadata(self):
        qtriples=[
                 ("?fooshout",po.shoutText,"?text"),
                 ]
        totalchars=sum(                self.size_chars_overall)
        mchars_messages=n.mean(        self.size_chars_overall)
        dchars_messages=n.std(         self.size_chars_overall)
        totaltokens=sum(              self.size_tokens_overall)
        mtokens_messages=n.mean(      self.size_tokens_overall)
        dtokens_messages=n.std(       self.size_tokens_overall)
        totalsentences=sum(        self.size_sentences_overall)
        msentences_messages=n.mean(self.size_sentences_overall)
        dsentences_messages=n.std( self.size_sentences_overall)
        nmessages=P.get("SELECT (COUNT(?s) as ?s) WHERE { ?s a po:Shout }",context=self.translation_graph)
        nparticipants=P.get("SELECT (COUNT(?s) as ?s) WHERE { ?s a po:Participant }",context=self.translation_graph)
        triples=[
                (self.snapshoturi, po.nParticipants,     nparticipants),
                (self.snapshoturi, po.nMessages,         nmessages),
                (self.snapshoturi, po.nCharsOverall,     totalchars),
                (self.snapshoturi, po.mCharsOverall,     mchars_messages),
                (self.snapshoturi, po.dCharsOverall,     dchars_messages),
                (self.snapshoturi, po.nTokensOverall,    totaltokens),
                (self.snapshoturi, po.mTokensOverall,    mtokens_messages),
                (self.snapshoturi, po.dTokensOverall,    dtokens_messages),
                (self.snapshoturi, po.nSentencesOverall, totalsentences),
                (self.snapshoturi, po.mSentencesOverall, msentences_messages),
                (self.snapshoturi, po.dSentencesOverall, dsentences_messages),
                ]
        P.add(triples,context=self.meta_graph)
        P.rdf.triplesScaffolding(self.snapshoturi,
                [po.ParticipantAttribute]*len(self.participantvars),
                self.participantvars,context=self.meta_graph)
        P.rdf.triplesScaffolding(self.snapshoturi,
                [po.MessageAttribute]*len(self.messagevars),
                self.messagevars,context=self.meta_graph)
        P.rdf.triplesScaffolding(self.snapshoturi,
                [po.shoutXMLFilename]*len(self.translation_xml)+[po.shoutTTLFilename]*len(self.translation_ttl),
                self.translation_xml+self.translation_ttl,context=self.meta_graph)
        P.rdf.triplesScaffolding(self.snapshoturi,
                [po.onlineShoutXMLFile]*len(self.translation_xml)+[po.onlineShoutTTLFile]*len(self.translation_ttl),
                [self.online_prefix+i for i in self.translation_xml+self.translation_ttl],context=self.meta_graph)

        self.mrdf=self.snapshotid+"Meta.rdf"
        self.mttl=self.snapshotid+"Meta.ttl"
        self.desc="irc dataset with snapshotID: {}\nsnapshotURI: {} \nisEgo: {}. isGroup: {}.".format(
                                                self.snapshotid,self.snapshoturi,self.isego,self.isgroup,)
        self.desc+="\nisFriendship: {}; ".format(self.isfriendship)
        self.desc+="isInteraction: {}.".format(self.isinteraction)
        self.nchecks=P.get(r"SELECT (COUNT(?checker) as ?cs) WHERE { ?foosession po:checkParticipant ?checker}",context=self.translation_graph)
        self.desc+="\nnParticipants: {}; nInteractions: {} (only session checks in first aa).".format(self.nparticipants,self.ncheckers)
        self.desc+="\nisPost: {} (alias hasText: {})".format(self.hastext,self.hastext)
        self.desc+="\nnMessages: {}; ".format(self.nmessages)

        self.desc+="\nnCharsOverall: {}; mCharsOverall: {}; dCharsOverall: {}.".format(self.totalchars,self.mcharsmessages,self.dcharsmessages)
        self.desc+="\nnTokensOverall: {}; mTokensOverall: {}; dTokensOverall: {};".format(self.totaltokens,self.mtokensmessages,self.dtokensmessages)
        self.desc+="\nnSentencesOverall: {}; mSentencesOverall: {}; dSentencesOverall: {};".format(self.totalsentences,self.msentencesmessages,self.dsentencesmessages)
        self.desc+="\nnURLs: {}; nAAMessages {}.".format(self.nurls,self.naamessages)
        triples=[
                (self.snapshoturi, po.triplifiedIn,      datetime.datetime.now()),
                (self.snapshoturi, po.triplifiedBy,      "scripts/"),
                (self.snapshoturi, po.donatedBy,         self.snapshotid[:-4]),
                (self.snapshoturi, po.availableAt,       self.online_prefix),
                (self.snapshoturi, po.onlineMetaXMLFile, self.online_prefix+self.mrdf),
                (self.snapshoturi, po.onlineMetaTTLFile, self.online_prefix+self.mttl),
                (self.snapshoturi, po.metaXMLFileName,   self.mrdf),
                (self.snapshoturi, po.metaTTLFileName,   self.mttl),
                (self.snapshoturi, po.totalXMLFileSizeMB, sum(self.size_xml)),
                (self.snapshoturi, po.totalTTLFileSizeMB, sum(self.size_ttl)),
                (self.snapshoturi, po.acquiredThrough,   "aa shouts in "+self.snapshotid),
                (self.snapshoturi, po.socialProtocolTag, "AA"),
                (self.snapshoturi, po.socialProtocol,    P.rdf.ic(po.Platform,"IRC",self.meta_graph,self.snapshoturi)),
                (self.snapshoturi, po.nTriples,         self.ntriples),
                (self.snapshoturi, NS.rdfs.comment,         self.desc),
                ]
        P.add(triples,self.meta_graph)

    def writeAll(self):
        g=P.context(self.meta_graph)
        ntriples=len(g)
        triples=[
                 (self.snapshoturi,po.nMetaTriples,ntriples)      ,
                 ]
        P.add(triples,context=self.meta_graph)
        g.namespace_manager.bind("po",po)
        g.serialize(self.final_path_+self.snapshotid+"Meta.ttl","turtle"); c("ttl")
        g.serialize(self.final_path_+self.snapshotid+"Meta.rdf","xml")
        c("serialized meta")
        if not os.path.isdir(self.final_path_+"scripts"):
            os.mkdir(self.final_path_+"scripts")
        shutil.copy(S.PACKAGEDIR+"/../tests/triplify.py",self.final_path_+"scripts/triplify.py")
        # copia do base data
        tinteraction="""\n\n{} individuals with metadata {}
and {} interactions (direct messages: {}, user mentions: {}) 
constitute the interaction 
structure in the RDF/XML file(s):
{}
and the Turtle file(s):
{}
(anonymized: "nicks inteface").""".format( self.nparticipants,str(self.participantvars),
                    self.ndirect+self.nmention,self.ndirect,self.nmention,
                    self.log_xml,
                    self.log_ttl)
        tposts="""\n\nThe dataset consists of {} irc messages with metadata {}
{:.3f} characters in average (std: {:.3f}) and total chars in snapshot: {}
{:.3f} tokens in average (std: {:.3f}) and total tokens in snapshot: {}
{:.3f} sentences in average (std: {:.3f}) and total sentences in snapshot: {}""".format(
                        self.nmessages,str(self.messagevars),
                         self.mcharsmessages, self.dcharsmessages,self.totalchars,
                        self.mtokensmessages,self.dtokensmessages,self.totaltokens,
                        self.msentencesmessages,self.dsentencesmessages,self.totalsentences,
                        )
        self.dates=[i.isoformat() for i in self.dates]
        date1=min(self.dates)
        date2=max(self.dates)
        with open(self.final_path_+"README","w") as f:
            f.write("""::: Open Linked Social Data publication
\nThis repository is a RDF data expression of the IRC
snapshot {snapid} with tweets from {date1} to {date2}
(total of {ntrip} triples).{tinteraction}{tposts}
\nMetadata for discovery in the RDF/XML file:
{mrdf} \nor in the Turtle file:\n{mttl}
\nEgo network: {ise}
Group network: {isg}
Friendship network: {isf}
Interaction network: {isi}
Has text/posts: {ist}
\nAll files should be available at the git repository:
{ava}
\n{desc}

The script that rendered this data publication is on the script/ directory.\n:::""".format(
                snapid=self.snapshotid,date1=date1,date2=date2,ntrip=self.ntriples,
                        tinteraction=tinteraction,
                        tposts=tposts,
                        mrdf=self.log_xml,
                        mttl=self.log_ttl,
                        ise=self.isego,
                        isg=self.isgroup,
                        isf=self.isfriendship,
                        isi=self.isinteraction,
                        ist=self.hastext,
                        ava=self.online_prefix,
                        desc=self.desc
                        ))

    def addShout(self,shouturi,shouttext):
        size_chars=len(shouttext)
        size_tokens=len(k.wordpunct_tokenize(shouttext))
        size_sentences=len(k.sent_tokenize(shouttext))
        triples=[
                (shouturi, po.shoutMessage, shouttext),
                (shouturi, po.nChars,       size_chars),
                (shouturi, po.nTokens,      size_tokens),
                (shouturi, po.nSentences,   size_sentences),
                ]
        self.size_chars_overall+=[size_chars]
        self.size_tokens_overall+=[size_tokens]
        self.size_sentences_overall+=[size_sentences]
        return triples
    def writeTranslates(self,mode="full"):
        c("mode full or chunk or multigraph write:",mode)
        if mode=="full":
            g=P.context(self.translation_graph)
            self.translation_ttl=self.snapshotid+"Translation.ttl"
            self.translation_xml=self.snapshotid+"Translation.rdf"
            g.serialize(self.final_path_+self.translation_ttl,"turtle"); c("ttl")
            g.serialize(self.final_path_+self.translation_xml,"xml")
        elif mode=="chunk":
            # writeByChunks
            raise NotImplementedError("Perform P.utils.writeByChunks on self.translation_graph")
        elif mode=="multigraph":
            raise NotImplementedError("Perform serialize(write) on each of the self.translation_graphs")


