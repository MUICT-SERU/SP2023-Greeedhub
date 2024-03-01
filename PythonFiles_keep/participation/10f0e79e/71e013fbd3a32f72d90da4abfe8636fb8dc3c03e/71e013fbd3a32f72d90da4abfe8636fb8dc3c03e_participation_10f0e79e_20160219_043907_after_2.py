import percolation as P, rdflib as r, urllib
from percolation.rdf import NS,po,a,c
from percolation.rdf.publishing import TranslationPublishing

class ParticipabrPublishing(TranslationPublishing):
    snapshotid="participabr-legacy"
    translation_graph="participabr-translation"
    meta_graph="participabr-meta"
    def __init__(self,postgresql_cursor):
        snapshoturi=P.rdf.ic(po.ParticipabrSnapshot,self.snapshotid,self.translation_graph)
        P.add((snapshoturi,a,po.Snapshot),context=self.translation_graph)
        cur=postgresql_cursor
        self.getData(cur)
        self.translateToRdf()
    def translateToRdf(self):
        triples=[]
        for pp in self.profiles:
            ### tabela profiles
            return
            ind=opa.Member+"#"+Q_("identifier")
            G(ind,rdf.type,opa.Member)
            G( ind,opa.name, L(Q("name"),xsd.string) )
            q=Q("type")
            if q=="Person":
                G(ind,rdf.type,opa.Participant)
                G( ind,opa.mbox,U("mailto:%s"%(Qu("email"),)) )
            elif q=="Community": G(ind,rdf.type,opa.Group)
            else:
                G(ind,rdf.type,opa.Organization)
            
            G(ind,opa.visibleProfile, L(Q("visible"),xsd.boolean) )
            G(ind,opa.publicProfile, L(Q("public_profile"),xsd.boolean))
            if Q("lat") and Q("lng"):
                lugar=r.BNode()
                G(lugar,rdf.type,opa.Point )
                G(ind, opa.based_near, lugar )
                G(lugar,opa.lat, L(Q("lat"),xsd.float))
                G(lugar,opa.long,L(Q("lng"),xsd.float))

            G(ind,opa.created,L(Q("created_at"),xsd.dateTime))
            G(ind,opa.modified,L(Q("updated_at"),xsd.dateTime))
            # campo composto
            campos=fparse(Q("data"))
            if "city" in campos.keys():
                cid=campos["city"]
                if cid:
                    G(ind,opa.city,L(cid,xsd.string))
            if "country" in campos.keys():
                cid=campos["country"]
                if cid:
                    G(ind,opa.country,L(cid,xsd.string))
            if "state" in campos.keys():
                cid=campos["state"]
                if cid:
                    G(ind,opa.state,L(cid,xsd.string))
            if "professional_activity" in campos.keys():
                cid=campos["professional_activity"]
                if cid:
                    G(ind,opa.professionalActivity,L(cid,xsd.string))
            if "organization" in campos.keys():
                cid=campos["organization"]
                if cid:
                    G(ind,opa.organization,L(cid,xsd.string))


            ### tabela artigos
            profile_id=Q("id")
            AA=[i for i in articles if i[AN.index("profile_id")]==profile_id]
            for aa in AA:
                if QA("published") and Q("public_profile"):
                    ART = opa.Article+"#"+str(QA("id"))
                    G(ART,rdf.type,opa.Article)
                    G(ART,opa.publisher,ind)
                    tipo=QA("type")
                    G(ART,opa.atype,L(tipo,xsd.string))
                    if sum([foo in tipo for foo in ["::","Article","Event","Blog"]]):
                        name=QA("name")
                        if name !="Blog":
                            G(ART,opa.title,L(name,xsd.string))
                        if tipo=='CommunityTrackPlugin::Track':
                            G(ART,opa.atype,opa.ParticipationTrack)
                        if tipo=='CommunityTrackPlugin::Step':
                            G(ART,opa.atype,opa.ParticipationStep)
                            pid=QA("parent_id")
                            aa2=[xx for xx in articles if xx[AN.index("id")]==pid][0]
                            pid=aa2[AN.index("profile_id")]  # o pid é o mesmo sempre!
                            pp2=[xx for xx in profiles if xx[PN.index("id")]==pid][0]
                            ART2 = opa.Article+"#"+str(aa2[AN.index("id")])
                            G(ART2,opa.hasStep,ART)
                    body=QA("body")
                    if (body!=None) and ( not body.startswith("--- ")):
                        G(ART,opa.body,L(remove_tags(body),xsd.string) )
                    abst=QA("abstract")
                    if abst:
                        G( ART,opa.abstract,L(remove_tags(abst),xsd.string) )
                    G(ART,opa.created,L( QA("created_at"),xsd.dateTime))
                    G(ART,opa.modified,L(QA("updated_at"),xsd.dateTime))
                    G(ART,opa.published,L(QA("published_at"),xsd.dateTime))

            ### tabela comentários
            CC=[i for i in comments if i[CN.index("author_id")]==profile_id]
            for cc in CC:
                COM=opa.Comment+"#"+str(QC("id"))
                G(COM,rdf.type,opa.Comment)
                G(COM,opa.creator,ind)
                if cc[CN.index("title")]:
                    G(COM,opa.title,L(QC("title"),xsd.string))
                G(COM,opa.body,L(remove_tags(QC("body")),xsd.string))
                G(COM,opa.created,L(QC("created_at"),xsd.dateTime))
                if QC("source_type")!="ActionTracker::Record":
                    ART=QC("referrer")
                    if ART:
                        ART = opa.Article+"#"+str(QC("source_id")) # VERIFICAR
                        G(ART,opa.hasReply,COM)

                    rip=str(QC("reply_of_id"))
                    if rip:
                        turi=opa.Comment+"#"+rip
                        G(turi , opa.hasReply , COM )

                    G(COM,opa.ip,L(QC("ip_address"),xsd.string))

        ### tabela friendships
        AM=[]
        for fr in friendships:
            fid1=QF("person_id")
            fid2=QF("friend_id")
            am=set([fid1,fid2])
            if am not in AM:
                AM.append(am)
                ind1,ind2=[(opa.Member+"#"+Q_("identifier")) for pp in profiles if pp[0] in am]
                g.add((ind1,opa.knows,ind2))
                tfr=opa.Friendship+"#"+("%s-%s"%tuple(am))
                G(tfr,rdf.type,opa.Friendship)
                G(tfr,opa.member,ind1)
                G(tfr,opa.member,ind2)
                G(ind1,opa.created,L(QF("created_at"),xsd.dateTime))

        for voto in votes:
            tfr=opa.Vote+"#"+str(voto[0])
            G(tfr,rdf.type,opa.Vote)
            G(tfr,opa.polarity,L(voto[1],xsd.boolean))
            if voto[3]=="Comment":
                uri=opa.Comment+"#"+str(voto[2])
            else:
                uri=opa.Article+"#"+str(voto[2])
            if voto[4]:
                ind=[(opa.Member+"#"+Q_("identifier")) for pp in profiles if pp[0]==voto[4]][0]
                G(tfr,opa.voter,ind)
            G(tfr,opa.created,L(voto[6],xsd.dateTime))

        for tag in tags:
            tfr=opa.Tag+"#"+str(tag[0])
            G(tfr,rdf.type,opa.Tag)
            G(tfr,opa.name,L(tag[1],xsd.string))

        for tt in taggings:
            tfr=opa.Tagging+"#"+str(tt[0])
            G(tfr,rdf.type,opa.Tagging)
            tag=opa.Tag+"#"+str(tt[1])
            G(tfr,opa.tag,tag)
            art=opa.Article+"#"+str(tt[2])
            G(tfr,opa.article,art)
            G(tfr,opa.created,L(tt[4],xsd.dateTime))
    def getData(self,cur):
        cur.execute('SELECT * FROM users')
        users = cur.fetchall()
        cur.execute('SELECT * FROM profiles')
        profiles = cur.fetchall()
        cur.execute('SELECT * FROM articles')
        articles = cur.fetchall()
        cur.execute('SELECT * FROM comments')
        comments = cur.fetchall()
        cur.execute('SELECT * FROM friendships')
        friendships= cur.fetchall()
        cur.execute('SELECT * FROM votes')
        votes= cur.fetchall()
        cur.execute('SELECT * FROM tags')
        tags= cur.fetchall()
        cur.execute('SELECT * FROM taggings')
        taggings= cur.fetchall()

        # nome das colunas nas tabelas
        cur.execute("select column_name from information_schema.columns where table_name='users';")
        users_columns=[i[0] for i in cur.fetchall()[::-1]]
        cur.execute("select column_name from information_schema.columns where table_name='profiles';")
        profiles_columns=[i[0] for i in cur.fetchall()[::-1]]
        cur.execute("select column_name from information_schema.columns where table_name='articles';")
        articles_columns=[i[0] for i in cur.fetchall()[::-1]]
        cur.execute("select column_name from information_schema.columns where table_name='comments';")
        comments_columns=[i[0] for i in cur.fetchall()[::-1]]
        cur.execute("select column_name from information_schema.columns where table_name='friendships';")
        friendships_columns=[i[0] for i in cur.fetchall()[::-1]]
        cur.execute("select column_name from information_schema.columns where table_name='votes';")
        votes_columns=[i[0] for i in cur.fetchall()[::-1]]
        cur.execute("select column_name from information_schema.columns where table_name='tags';")
        tags_columns=[i[0] for i in cur.fetchall()[::-1]]
        cur.execute("select column_name from information_schema.columns where table_name='taggings';")
        taggings_columns=[i[0] for i in cur.fetchall()[::-1]]
        locals_=locals().copy(); del locals_["self"]
        for i in locals_:
            exec("self.{}={}".format(i,i))

def fparse(mstring):
    foo=[i for i in mstring.split("\n")[1:-1] if i]
    return dict([[j.strip().replace('"',"") for j in i.split(":")[1:]] for i in foo if  len(i.split(":"))==3])
U=r.URIRef
QQ=urllib.parse.quote
def Q_(mstr):
    return QQ(pp[PN.index(mstr)])
def Q(mstr):
    return pp[PN.index(mstr)]
def QA(mstr):
    return aa[AN.index(mstr)]
def QC(mstr):
    return cc[CN.index(mstr)]

def QF(mstr):
    return fr[FRN.index(mstr)]
