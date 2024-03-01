import percolation as P, rdflib as r, urllib, datetime, re, codecs
from percolation.rdf import NS,po,a,c
from percolation.rdf.publishing import TranslationPublishing
import babel
from validate_email import validate_email
from bs4 import BeautifulSoup

class DataTable:
    def __init__(self,data_values,column_names):
        """data_values is an iterable of iterables, column_names is an iterable"""
        locals_=locals().copy(); del locals_["self"]
        for i in locals_:
            exec("self.{}={}".format(i,i))
    def get(self,column_name):
        index=self.column_names.index(column_name)
        return [i[index] for i in self.data_values]
    def getMany(self,column_names):
        indexes=[self.column_names.index(i) for i in column_names]
        return [[i[index] for index in indexes] for i in self.data_values]


class ParticipabrPublishing(TranslationPublishing):
    snapshotid="participabr-legacy"
    translation_graph="participabr-translation"
    meta_graph="participabr-meta"
    def __init__(self,postgresql_cursor):
        snapshoturi=P.rdf.ic(po.ParticipabrSnapshot,self.snapshotid,self.translation_graph)
        P.add((snapshoturi,a,po.Snapshot),context=self.translation_graph)
        cur=postgresql_cursor
        datas=[]; bodies=[]
        locals_=locals().copy(); del locals_["self"]
        for i in locals_:
            exec("self.{}={}".format(i,i))
        self.getData(cur)
        self.translateToRdf()
    def translateToRdf(self):
        triples=[]

        for identifier,name,type_,visible,public_profile,lat,lng,created_at,updated_at,data,id_\
        in self.profiles_table.getMany(["identifier","name","type","visible","public_profile","lat","lng","created_at","updated_at","data","id"]):
            break
            ### tabela profiles
            assert identifier.islower() or identifier.isdigit()
            participanturi=P.rdf.ic(po.Participant,self.snapshotid+"-"+identifier,self.translation_graph,self.snapshoturi)
            profileuri=P.rdf.ic(po.Profile,self.snapshotid+"-"+str(id_),self.translation_graph,self.snapshoturi)
            #c(identifier)
            assert bool(name)
            assert type_ in ("Person","Community","Enterprise")
            assert visible in (False,True)
            assert public_profile in (False,True)
            assert isinstance(created_at,datetime.datetime)
            assert isinstance(updated_at,datetime.datetime)
            triples+=[
                    (participanturi,po.name,name),
                    (participanturi,a,eval("po."+type_)),
                    (participanturi,po.profile,profileuri),
                    (profileuri,po.visible,visible),
                    (profileuri,po.public,public_profile),
                    (profileuri,po.createdAt,created_at),
                    (profileuri,po.updatedAt,updated_at),
                    ]
            assert isinstance(lat,(type(None),float))
            assert isinstance(lng,(type(None),float))
            assert type(lat)==type(lng)
            if lat:
                place=r.BNode()
                triples+=[
                        (participanturi,po.basedNear,place),
                        (place,po.latitude,lat),
                        (place,po.longitude,lng),
                        ]
            data_,triples_=parseData(data,participanturi)
            triples+=triples_
            for field in data_:
                triples+=[
                         (participanturi,eval("po."+field),data_[field])
                         ]
            self.datas+=[(data_,data)]
            email=self.emails.get(identifier)
            if email:
                assert validate_email(email)
                triples+=[
                         (participanturi,po.email,email),
                         ]
        c("finished triplification of profiles")
        #P.add(triples,self.translation_graph)
        c("finished profiles add to rdflib graph")
        triples=[]
        for profile_id,published,id_,type_,body,abstract,created_at,updated_at,published_at in\
        self.articles_table.getMany(("profile_id","published","id","type","body","abstract","created_at","updated_at","published_at")):
            identifier=self.profileids[profile_id]
            #c(identifier)
            participanturi=po.Participant+"#"+self.snapshotid+"-"+identifier
            #assert P.get(participanturi,po.name,context=self.translation_graph)
            #c(participanturi)
            articleuri=P.rdf.ic(po.Article,self.snapshotid+"-"+str(id_),self.translation_graph,self.snapshoturi)
            assert isinstance(created_at,datetime.datetime)
            assert isinstance(updated_at,datetime.datetime)
            assert isinstance(published_at,datetime.datetime)
            triples+=[
                     (articleuri,po.author,participanturi),
                     (articleuri,po.createdAt,created_at),
                     (articleuri,po.updatedAt,updated_at),
                     (articleuri,po.publishedAt,published_at),
                     (articleuri,po.published,published),
                     ]
            if not body or body.startswith("---") or body=='<p>artigo filho</p>' or body.strip().count(" ")<2:
                body=""
            if body:
                c("body:",body)
                if re.findall(r"<(.*)>(.*)<(.*)>",body,re.S):
                    rawbody=BeautifulSoup(body, 'html.parser').get_text()
                    triples+=[
                             (articleuri,po.htmlBodyText,body),
                             (articleuri,po.rawBodyText,body),
                             ]
                else:
                    triples+=[
                             (articleuri,po.rawBodyText,body),
                             ]
                self.bodies+=[body]
            continue
        c("finished triplification of articles")
        return
            ### tabela artigos
        for banana in ba:
            for aa in AA:
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
        return
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
        tables=("users",'profiles','articles','comments','friendships','votes','tags','taggings')
        for table in tables:
            #eval("{},{},{}=table_values,table_names,table_object")
            cur.execute('SELECT * FROM '+table)
            exec("{}_values=cur.fetchall()".format(table))
            cur.execute("select column_name from information_schema.columns where table_name='{}';".format(table))
            exec("{}_names=[i[0] for i in cur.fetchall()[::-1]]".format(table))
            exec("{}_table=DataTable({},{})".format(table,table+"_values",table+"_names"))
        emails=dict(locals()["users_table"].getMany(("login","email")))
        profileids=dict(locals()["profiles_table"].getMany(("id","identifier")))
        
        #emails=users_table.getMany(("email","login")) # ??? WHY WONT THIS WORK?? TTM
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
datafields={'acronym',
 'addressReference',
 'allowUnauthenticatedComments',
 'city',
 'closed',
 'contactEmail',
 'country',
 'description',
 'district',
 'enableContactUs',
 'fieldsPrivacy',
 'lastNotification',
 'layoutTemplate',
 'moderatedArticles',
 'notificationTime',
 'organization',
 'organizationWebsite',
 'professionalActivity',
 'redirectL10n',
 'state',
 'subOrganizationsPluginParentToBe',
 'tagList',
 'zipCode'}
def parseData(datastring,participanturi):
    #candidates=datastring.split("\n")
    countries=babel.Locale("pt").territories
    candidates=re.findall(r":(.*?): (.*)",datastring)
    data={}
    allowed={"acronym","contactEmail","description", "organizationWebsite","professionalActivity"}
    process={"addressReference", # remove "não tem" and all([i.lower()=="x" for i in ar])
            'allowUnauthenticatedComments',# bool(i)
            'city',# all([i.lower()=="-" for i in ar])
            "country", # babel.Locale("pt").territories
            "district",
            "organization",
            "state",
            "tagList"}
    removed={"closed","enableContactUs","fieldsPrivacy","lastNotification","layoutTemplate","moderatedArticles","notificationTime","subOrganizationsPluginParentToBe"}
    triples=[]
    for field,value in candidates:
        if value and field:
            if re.findall(r":"+field+r": \"",datastring):
                # field value in quotes:
                value=re.findall(r":"+field+r': \"(.*?)\".*(?:$|:.*:.*)',datastring,re.S)[0]
            value.strip()
            if not value.replace("\"",""):
                continue
            #value_=codecs.decode(value,"unicode_escape").encode("utf8").decode("latin1")
            value_=codecs.decode(value,"unicode_escape").encode("latin1").decode("utf8")
            field_=re.sub(r"_(.)",lambda m: m.groups()[0].upper(),field)
            assert field_ in datafields
            if field_ in allowed:
                pass
            elif field_=="addressReference" and (value_=="não tem" or value_.count("x")==len(value_)):
                continue
            elif field_=="zipCode" and (len(value_)==1 or value_=="não tem"):
                continue
            if field_=="tagList":
                field_="subjectMatter"
            if field_=="state" and "binary" in value_:
                continue
            if field_=="allowUnauthenticatedComments":
                value_=bool(value_)
            if field_=="organization" and \
            (value_.count("-")==len(value_) or value_.count("0")==len(value_) or value_.count(".")==len(value_) or value_.count("*")==len(value_)  or value_.count("?")==len(value_) or "binary" in value_ or "não tem"==value_):
                continue
            if field_=="district" and (value_.count("-")==len(value_) or "binary" in value_ or "não tem"==value_):
                continue
            if field_=="city" and (value_.count("-")==len(value_)):
                continue
            if field_=="country":
                if value_ in countries:
                    value_=countries[value_]
                elif value_.title() in countries.values():
                    value_=value.title()
                elif "binary" in value_:
                    continue
                elif 'Av. Deodoro da Fonseca' == value_:
                    continue
                elif 'Usa' == value_:
                    value_=countries["US"]
                elif 'Países Baixos' in value_:
                    value_="Holanda"
                elif '/' in value_:
                    countries=value_.split("/")
                    for country in countries:
                        triples+=[
                                 (participanturi,po.country,country),
                                 ]
            triples+=[
                     (participanturi,eval("po."+field_),value_),
                     ]
            data[field_]=value_
    return data,triples
    # check for all fields
    #check for correct encodings
    # for now: 

