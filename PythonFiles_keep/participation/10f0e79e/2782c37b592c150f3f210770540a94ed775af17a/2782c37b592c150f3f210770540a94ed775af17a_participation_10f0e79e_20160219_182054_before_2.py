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
        datas2=[]; datas=[]; bodies=[]
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
        for profile_id,published,id_,type_,body,abstract,creaed_at,updated_at,published_at,hits,start_date,end_date,parent_id,position,path,setting in\
        self.articles_table.getMany(("profile_id","published","id","type","body","abstract","created_at","updated_at","published_at","hits","start_date","end_date","parent_id","position","path","setting")):
            break
            identifier=self.profileids[profile_id]
            #c(identifier)
            participanturi=po.Participant+"#"+self.snapshotid+"-"+identifier
            #assert P.get(participanturi,po.name,context=self.translation_graph)
            #c(participanturi)
            type__=type_.split("::")[-1]
            articleuri=P.rdf.ic(eval("po."+type__),self.snapshotid+"-"+str(id_),self.translation_graph,self.snapshoturi)
            assert isinstance(created_at,datetime.datetime)
            assert isinstance(updated_at,datetime.datetime)
            assert isinstance(published_at,datetime.datetime)
            triples+=[
                     (articleuri,a,po.Article),
                     (articleuri,po.author,participanturi),
                     (articleuri,po.createdAt,created_at),
                     (articleuri,po.updatedAt,updated_at),
                     (articleuri,po.publishedAt,published_at),
                     (articleuri,po.published,published),
                     (articleuri,po.hits,hits),
                     (articleuri,po.path,path),
                     ]
            if not body or body.startswith("---") or body=='<p>artigo filho</p>' or body.strip().count(" ")<2:
                body=""
            if body:
#                c("body:",body)
                if re.findall(r"<(.*)>(.*)<(.*)>",body,re.S):
                    rawbody=BeautifulSoup(body, 'html.parser').get_text()
                    triples+=[
                             (articleuri,po.htmlBodyText,body),
                             (articleuri,po.cleanBodyText,body),
                             ]
                else:
                    triples+=[
                             (articleuri,po.cleanBodyText,body),
                             ]
                self.bodies+=[body]
            if abstract:
                if re.findall(r"<(.*)>(.*)<(.*)>",abstract,re.S):
                    rawbody=BeautifulSoup(abstract, 'html.parser').get_text()
                    triples+=[
                             (articleuri,po.htmlAbstractText,body),
                             (articleuri, po.cleanAbstractText,body),
                             ]
                else:
                    triples+=[
                             (articleuri,po.cleanAbstractText,body),
                             ]
            if parent_id:
                type2__=self.articletypes[parent_id].split("::")[-1]
                articleuri2=P.rdf.ic(eval("po."+type2__),self.snapshotid+"-"+str(parent_id),self.translation_graph,self.snapshoturi)
                triples+=[
                         (articleuri,po.parent,articleuri2),
                         ]
                if type__=="Step":
                    assert isinstance(position,int)
                    triples+=[
                             (articleuri,po.stepOf,articleuri2),
                             (articleuri,po.position,position),
                             ]
                elif type__=="Mediation":
                    triples+=[
                             (articleuri,po.mediationOf,articleuri2),
                             ]
            if start_date:
                #assert isinstance(start_date,datetime.datetime)
                assert isinstance(start_date,datetime.date)
                triples+=[
                         (articleuri,po.startAt,start_date),
                         ]
            if end_date:
                #assert isinstance(end_date,datetime.datetime)
                assert isinstance(end_date,datetime.date)
                triples+=[
                         (articleuri,po.endAt,end_date),
                         ]
            if setting:
                data2_,triples2_=parseData(setting,articleuri)
                triples+=triples2_
                self.datas2+=[(data2_,setting)]
            continue
        c("finished triplification of articles")
        for id_,title,body,created_at,reply_of_id,ip_address in self.comments_table.getMany(("id","title","body","created_at","reply_of_id","ip_address")):
            pass
        return
            ### tabela comentários
        for banana in feijao:
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
        articletypes=dict(locals()["articles_table"].getMany(("id","type")))
        
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
def parseData(datastring,participanturi,setting=False):
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
#            assert field_ in datafields
            if field_ in allowed:
                pass
            elif field_=="addressReference" and (value_=="não tem" or value_.count("x")==len(value_)):
                continue
            elif field_=="zipCode" and (len(value_)==1 or value_=="não tem"):
                continue
            elif field_=="tagList":
                field_="subjectMatter"
            elif field_=="state" and "binary" in value_:
                continue
            elif field_=="allowUnauthenticatedComments":
                value_=bool(value_)
            elif field_=="organization" and \
            (value_.count("-")==len(value_) or value_.count("0")==len(value_) or value_.count(".")==len(value_) or value_.count("*")==len(value_)  or value_.count("?")==len(value_) or "binary" in value_ or "não tem"==value_):
                continue
            elif field_=="district" and (value_.count("-")==len(value_) or "binary" in value_ or "não tem"==value_):
                continue
            elif field_=="city" and (value_.count("-")==len(value_)):
                continue
            elif field_=="country":
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
            if setting:
                if field_ in {"visualizationFOrmat","twitterConsumerKey","postsPerPage","displayHits","twitterConsumerSecret","displayPostsInCurrentLanguage","twitterAccessToken","twitterAccessTokenSecret","publishSubmissions","followers","displayVersions"}:
                    continue
                elif field_=="hashtagsTwitter":
                    field_="twitterHashtags"
                if field_=="twitterHashtags":
                    hashtags=value_.split(",")
                    for hashtag in hashtags:
                        triples+=[
                                 (participanturi,po.hashtag,hashtag.strip()),
                                 ]
                    continue
            if value_ in ('true','false'):
                value_=(False,True)[value_=='true']
            triples+=[
                     (participanturi,eval("po."+field_),value_),
                     ]
            data[field_]=value_
    return data,triples
    # check for all fields
    #check for correct encodings
    # for now: 

