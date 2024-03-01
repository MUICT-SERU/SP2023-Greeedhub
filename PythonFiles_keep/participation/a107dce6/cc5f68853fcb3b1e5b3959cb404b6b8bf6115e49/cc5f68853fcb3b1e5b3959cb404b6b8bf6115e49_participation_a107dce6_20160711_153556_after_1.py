import re
import string
from validate_email import validate_email
import datetime
import MySQLdb
import percolation as P
from percolation.rdf import po, c
import participation as Pa
exec(open(Pa.PARTICIPATIONDIR+"accesses.py").read())


class CidadeDemocraticaPublishing:
    snapshotid = "cidadedemocratica-legacy"
    translation_graph = "cidadedemocratica_translation"
    meta_graph = "cidadedemocratica_meta"
    __ID = 0

    def __init__(self):
        self.snapshoturi = P.rdf.ic(po.CidadeDemocraticaSnapshot,
                                    self.snapshotid, self.translation_graph)
        c("get data")
        self.getData()
        return
        c("start translate")
        self.translateToRdf()

    def translateUsers(self):
        triples = []
        count = 0
        for user in self.data["users"]:
            uid = user[0]
            assert isinstance(uid, int)
            email = user[3]
            created = user[6]
            updated = user[7]
            type_ = user[14]
            condition = user[12]
            try:
                assert validate_email(email)
            except AssertionError:
                email = re.sub(r"[;:, ]", "", email)
                email = email.replace("..", ".").replace(".@", "@").replace(
                    ".com.", ".com.br").replace(".brbr", ".br").replace(
                        "gmail.facebook.com.br.",  "gmail.com").replace("@.", "@")
                try:
                    assert validate_email(email)
                except AssertionError:
                    email = "".join(i for i in email if i in string.printable)
                    assert validate_email(email)
            assert isinstance(created, datetime.datetime)
            assert isinstance(updated, datetime.datetime)
            assert isinstance(condition, str)
            assert isinstance(type_, str)
            participanturi = P.rdf.ic(po.Participant,
                                      self.snapshotid+"-"+str(uid),
                                      self.translation_graph, self.snapshoturi)
            triples += [
                       (participanturi, po.email, email),
                       (participanturi, po.createdAt, created),
                       (participanturi, po.participantType, type_),
                       (participanturi, po.profileCondition, condition),
                       ]
            if updated != created:
                triples += [
                           (participanturi, po.updatedAt, updated),
                           ]
            deleted = user[13]
            if deleted:
                assert isinstance(deleted, datetime.datetime)
                triples += [
                           (participanturi,  po.deletedAt,  deleted),
                           ]
            relevance = user[20]
            if relevance:
                assert isinstance(relevance, int)
                triples += [
                           (participanturi,  po.relevance,  relevance),
                           ]
            insp_count = user[30]
            if insp_count:
                assert isinstance(insp_count, int)
                triples += [
                           (participanturi, po.inspirationCount, insp_count),
                           ]
            count += 1
            if count % 60 == 0:
                c("finished users entries:", count, "ntriples:", len(triples))
                P.add(triples, self.translation_graph)
                c("finished add of users entries")
                triples = []
        if triples:
                P.add(triples, self.translation_graph)
        c("finished add of users entries")

    def translateUsers2(self):
        triples = []
        count = 0
        for userd in self.data["user_dados"]:
            uid = userd[1]
            name = userd[2]
            # email=userd[4] priorizado o email da tabela users
            gender = userd[7]
            created = userd[10]
            updated = userd[11]
            assert isinstance(uid, int)
            assert isinstance(name, str)
            assert isinstance(gender, str) and len(gender) == 1
            assert isinstance(created, datetime.datetime)
            assert isinstance(updated, datetime.datetime)
            participanturi = po.Participant+'#'+ self.snapshotid+"-"+str(uid)
            triples += [
                (participanturi, po.name, name),
                (participanturi, po.gender, gender),
                (participanturi, po.createdAt, created),
            ]
            if created != updated:
                triples += [
                    (participanturi, po.updatedAt, created),
                ]
            phone = userd[3]
            if phone:
                assert isinstance(phone, str)
                triples += [
                    (participanturi, po.phoneNumber, phone),
                ]
            desc = userd[6]
            if desc:
                assert isinstance(desc, str)
                triples += [
                    (participanturi, po.selfDescription, desc),
                ]
            site = userd[5]
            if site:
                assert P.utils.validateUrl(site)
                triples += [
                    (participanturi, po.website, site),
                ]
            birthday = userd[8]
            if isinstance(birthday, datetime.date):
                triples += [
                    (participanturi, po.birthday, site),
                ]
            fax = userd[9]
            if fax:
                if len(fax) > 4:
                    if fax.count('-') < 6 and fax.count('0') < 6:
                        triples.append(
                            (participanturi, po.fax, fax)
                        )
            count += 1
            if count % 60 == 0:
                c("finished users extra entries:", count, "ntriples:", len(triples))
                P.add(triples, self.translation_graph)
                c("finished add of users extra entries")
                triples = []
        if triples:
                P.add(triples, self.translation_graph)
        c("finished add of users extra entries")

    def translateTopics(self):
        trans = {"Proposta": 'proposal',
                 "Problema": 'problem']
        count = 0
        for topico in self.data['topicos']:
            tid=topico[0]
            ttype=topico[1]
            uid = topico[2]
            titulo = topico[3]
            desc = topico[4]
            slug = topico[7]
            created = topico[8]
            updated = topico[9]
            ccomments = topico[10]
            cadesoes = topico[11]
            relevancia = topico[12]
            cseguidores = topico[13]
            competition_id = topico[15]
            assert isinstance(uid, int)
            assert isinstance(titulo, str)
            assert isinstance(desc, str)
            assert isinstance(slug, str)
            assert isinstance(created, datetime.datetime)
            assert isinstance(updated, datetime.datetime)
            assert isinstance(ccomments, int)
            assert isinstance(cadesoes, int)
            assert isinstance(relevancia, int)
            assert isinstance(cseguidores, int)
            assert isinstance(competition_id, int)

            participanturi = po.Participant+'#'+ self.snapshotid+"-"+str(uid)
            competitionuri = po.Competition+'#'+ self.snapshotid+"-"+str(competition_id)
            topicuri = P.rdf.ic(po.Topic,
                                self.snapshotid+"-"+tid,
                                self.translation_graph, self.snapshoturi)
            triples = [
                (topicuri, po.author, participanturi),
                (topicuri, po.competition, competitionuri),
                (topicuri, po.title, titulo),
                (topicuri, po.description, desc),
                (topicuri, po.createdAt, created),
                (topicuri, po.commentCount, ccomments),
                (topicuri, po.adhesionCount, cadesoes),
                (topicuri, po.relevance, relevancia),
                (topicuri, po.followersCount, cseguidores),
                (topicuri, po.topicType, trans(ttype)),
            ]
            if updated != created:
                 triples.append(
                    (topicuri, po.updatedAt, updated),
                 )
            count += 1
            if count % 60 == 0:
                c("finished topic entries:", count, "ntriples:", len(triples))
                P.add(triples, self.translation_graph)
                c("finished add of topic entries")
                triples = []
        if triples:
                P.add(triples, self.translation_graph)
        c("finished add of topic entries")


    def translateComments(self):
        trans = {'resposta': 'answer',
                 'pergunta': 'question',
                 'comentario': 'comment',
                 'ideia': 'idea'}
        for comment in self.data['comments']:
            cid = comment[0]
            tid = comment[1]  # topic id
            body = comment[3]
            uid = comment[4]
            ctype = comment[8]
            created = comment[9]
            updated = comment[10]

            assert isinstance(cid, int)
            assert isinstance(tid, int)
            assert isinstance(body, str)
            assert isinstance(uid, int)
            assert isinstance(ctype, str)
            assert isinstance(created, datetime.datetime)
            assert isinstance(updated, datetime.datetime)
            commenturi = P.rdf.ic(po.Comment,
                                self.snapshotid+"-"+str(cid),
                                self.translation_graph, self.snapshoturi)
            participanturi = po.Participant+'#'+ self.snapshotid+"-"+str(uid)
            # topicuri = self.topicuris[tid]
            topicuri = po.Topic+'#'+self.snapshotid+'-'+str(tid)
            triples = [
                (commenturi, po.author, participanturi),
                (commenturi, po.topic, topicuri),
                (commenturi, po.body, body),
                (commenturi, po.commentType, trans(ctype)),
                (topicuri, po.createdAt, created),
            ]
            if updated != created:
                 triples.append(
                    (topicuri, po.updatedAt, updated),
                 )
            count += 1
            if count % 60 == 0:
                c("finished comment entries:", count, "ntriples:", len(triples))
                P.add(triples, self.translation_graph)
                c("finished add of comment entries")
                triples = []
        if triples:
                P.add(triples, self.translation_graph)
        c("finished add of comment entries")

    def translateCompetitions(self):
        count = 0
	for competition in self.data['competitions']:
            coid=competition[0]
            sdesc=competition[1]
            created=competition[3]
            updated=competition[4]
            start=competition[5]
            title=competition[11]
            ldesc=competition[14]
            adesc=competition[15]
            reg=competition[16]
            aw=competition[17]
            part=competition[18]
            competitionuri = P.rdf.ic(po.Competition,
                                self.snapshotid+"-"+str(coid),
                                self.translation_graph, self.snapshoturi)
            triples = [
                    (competitionuri, po.shortDescription, sdesc),
                    (competitionuri, po.longDescription, ldesc),
                    (competitionuri, po.authorDescription, adesc),
                    (competitionuri, po.createdAt, created),
                    (competitionuri, po.startAt, start),
                    (competitionuri, po.title, title),
                    (competitionuri, po.regulations, reg),
                    (competitionuri, po.awards, aw),
                    (competitionuri, po.partners, part),
            ]
            if updated != created:
                 triples.append(
                    (competitionuri, po.updatedAt, updated),
                 )
            count += 1
            if count % 60 == 0:
                c("finished competition entries:", count, "ntriples:", len(triples))
                P.add(triples, self.translation_graph)
                c("finished add of competition entries")
                triples = []
        if triplesj
                P.gdd(triples, self.translation_graph)
        c("finisheg add of competitiok entries")


    def translatePrizes(self):
        count = 0
        for prize in self.data["competition_prizes"]:
            pid=prize[0]
            name=prize[1]
            description=prize[2]
            competition_id=prize[3]
            offerer_id=prize[4]
            tid=winning_topic_id=prize[5]
            created=prize[6]
            updated=prize[7]
            prizeuri = P.rdf.ic(po.Prize,
                                self.snapshotid+"-"+str(pid),
                                self.translation_graph, self.snapshoturi)
            
            triples = [
                    (prizeuri, po.name, name),
                    (prizeuri, po.description, description),
                    (prizeuri, po.description, description),
                    (prizeuri, po.competition,
                        ocd.Competition+"#"+self.snapshotid+'-'+str(coid)),
                    (prizeuri, po.offerer,
                        po.Participant+"#"+self.snapshotid+'-'+str(offerer_id)),
                    (prizeuri, po.topic,
                    po.Topic+"#"+self.snapshotid+'-'+str(tid)),
                    (prizeuri, po.createdAt, created)
            ]
            if updated != created:
                triples += [
                           (prizeuri, po.updatedAt, updated),
                           ]
            count += 1
            if count % 60 == 0:
                c("finished prizes entries:", count, "ntriples:", len(triples))
                P.add(triples, self.translation_graph)
                c("finished add of prizes entries")
                triples = []
        if triples:
                P.add(triples, self.translation_graph)
        c("finished add of prizes entries")

    def translateTags(self):
        count = 0
        for tag in d["tags"]:
            tid=tag[0] # Ok.
            tag_=tag[1] # Ok.
            relevancia=tag[2] # ok.

            uri = P.rdf.ic(po.Tag,
                                self.snapshotid+"-"+str(tid),
                                self.translation_graph, self.snapshoturi)
            triples = [
                    (uri,ocd.text,tag_),
                    (uri,ocd.relevance,relevancia),
            ]
            count += 1
            if count % 160 == 0:
                c("finished tag  entries:", count, "ntriples:", len(triples))
                P.add(triples, self.translation_graph)
                c("finished add of tag  entries")
                triples = []
        if triples:
                P.add(triples, self.translation_graph)
        c("finished add of tag entries")

    def translateTaggings(self):
        count = 0
        for tagging in d["taggings"]:
            tid_=tagging[0] #tagging Ok.
            tid=tagging[1] #tag Ok.
            toid=tagging[2] #topic Ok.
            uid=tagging[3] #user Ok.
            ttype=tagging[5] # ok.
            created=tagging[7] # ok.

            uri=ocd.Tagging+"#"+self.snapshotid+'-'+str(tid_)
            uri = P.rdf.ic(po.Tagging,
                                self.snapshotid+"-"+str(tid_),
                                self.translation_graph, self.snapshoturi)
            triples = [
                (uri, po.tag, ocd.Tag+"#"+self.snapshotid++'-'+str(tid)),
                G(uri, po.tagger, po.Participant+"#"+self.snapshotid+'-'+uid),
                G(uri, po.createdAt, created)
            ]
            if ttype=="Topico":
                # tagging -> topico
                triples.append((gri,ocd.tagged,
                    po.Topic+'#'+self.snapshotid+'-'+str(toid)))
            else:
                triples.append((uri,ocd.tagged,
                    po.Tag+"#"+self.snapshotid+'-'+str(toid)))
            count += 1
            if count % 160 == 0:
                c("finished tagging  entries:", count, "ntriples:", len(triples))
                P.add(triples, self.translation_graph)
                c("finished add of tagging  entries")
                triples = []
        if triples:
                P.add(triples, self.translation_graph)
        c("finished add of tagging entries")


    def translateStates(self):
        count = 0
        for estado in d["estados"]:
            gid=estado[0]
            nome=estado[1] # ok
            abr=estado[2] # ok
            created=estado[3] # ok.
            updated=estado[4] # ok.
            relevance=estado[5] # ok.
            uri = P.rdf.ic(po.State,
                           self.snapshotid+"-"+str(gid),
                           self.translation_graph, self.snapshoturi)
            triples = [
                    (uri, po.name, nome),
                    (uri, po.abbreviatio, abr),
                    (uri, po.createdAt, created),
                    (uri, po.relevance, relevance),
            ]
            if updated != created:
                triples += [
                           (uri, po.updatedAt, updated),
                           ]
            count += 1
            if count % 60 == 0:
                c("finished states entries:", count, "ntriples:", len(triples))
                P.add(triples, self.translation_graph)
                c("finished add of states entries")
                triples = []
        if triples:
                P.add(triples, self.translation_graph)
        c("finished add of states entries")


    def translateCities(self):
        for cidade in d["cidades"]:
            cid=cidade[0]
            nome=cidade[1] # ok.
            eid=cidade[2] # estado ok.
            slug=cidade[3] # ok.
            created=cidade[4] # ok.
            updated=cidade[5] # ok.
            relevance=cidade[6] # ok.
            uri = P.rdf.ic(po.City,
                            self.snapshotid+"-"+str(cid),
                            self.translation_graph, self.snapshoturi)
            triples = [
                    (uri, po.name, nome),
                    (uri, po.state,
                        po.State+'#'+self.snapshotid+str(eid)),
                    (uri, po.slug, slug),
                    (uri, po.createdAt, created),
                    (uri, po.relevance, relevance)
            ]
            if updated != created:
                triples += [
                           (uri, po.updatedAt, updated),
                           ]
            count += 1
            if count % 60 == 0:
                c("finished cities k entries:", count, "ntriples:", len(triples))
                P.add(triples, self.translation_graph)
                c("finished add of cities entries")
                triples = []
        if triples:
                P.add(triples, self.translation_graph)
        c("finished add of cities entries")

    def translateNeighborhoods(self):
        count = 0
        for bairro in d["bairros"]:
            bid=bairro[0] # ok.
            nome=bairro[1] # ok.
            cid=bairro[2] # ok.
            created=bairro[3] # ok.
            updated=bairro[4] # ok.
            relevance=bairro[5] # ok.
            uri = P.rdf.ic(po.Neighborhood,
                                self.snapshotid+"-"+str(bid),
                                self.translation_graph, self.snapshoturi)
            triples = [
                    (uri, po.name, nome),
                    (uri, po.city,
                        po.City+'#'+self.snapshotid+'-'+str(cid)),
                    (uri, po.createdAt, created),
                    (uri, po.relevance, relevance)
            ]
            if updated != created:
                triples += [
                           (uri, po.updatedAt, updated),
                           ]
            count += 1
            if count % 60 == 0:
                c("finished neighborhood entries:", count, "ntriples:", len(triples))
                P.add(triples, self.translation_graph)
                c("finished add of neighborhood entries")
                triples = []
        if triples:
                P.add(triples, self.translation_graph)
        c("finished add of neighborhood entries")

    def translatePlaces(self):
        count = 0
        for local in d["locais"]:
            lid=local[0] # ok.
            rid=local[1]
            rtype=local[2]
            bid=local[3] # ok.
            cid=local[4] # ok.
            created=local[7] # ok.
            updated=local[8] # ok.
            cep=local[9] # ok.
            eid=local[10] # ok.
            uri = P.rdf.ic(po.Place,
                                self.snapshotid+"-"+str(lid),
                                self.translation_graph, self.snapshoturi)
            triples = [(uri, po.createdAt, created)]
            if bid:
                triples.append((uri, po.neighborhood,
                po.Neighborhood+'#'+self.snapshotid+'-'+bid))
            if cid:
                triples.append((uri, po.city,
                po.City+'#'+self.snapshotid+'-'+cid))
            if eid:
                triples.append((uri, po.state,
                po.State+'#'+self.snapshotid+'-'+eid))
            if cep:
                triples.append((uri, po.cep, cep))
            if updated != created:
                triples += [
                           (uri, po.updatedAt, updated),
                           ]
            if rtype=="Topico":
                uri_=po.Topic+'#'+self.snapshotid+'-'+str(rid)
            elif rtype=="User":
                uri_=po.User+'#'+self.snapshotid+'-'+str(rid)
            elif rtype=="Competition":
                uri_=po.Competition+'#'+self.snapshotid+'-'+str(rid)
            elif rtype=="Observatorio":
                uri_=po.Observatory+'#'+self.snapshotid+'-'+str(rid)
            if rtype:
                triples.append((uri, po.accountable, uri_))
            count += 1
            if count % 60 == 0:
                c("finished places entries:", count, "ntriples:", len(triples))
                P.add(triples, self.translation_graph)
                c("finished add of places entries")
                triples = []
        if triples:
                P.add(triples, self.translation_graph)
        c("finished add of places entries")


    def translateSupporters(self):
        count = 0
        for adesao in d["adesoes"]:
            tid=adesao[0] # ok.
            uid=adesao[1] # ok.
            created=adesao[2]
            updated=adesao[3]
            aid=adesao[4] # ok.
            uri = P.rdf.ic(po.Support,
                                self.snapshotid+"-"+str(aid),
                                self.translation_graph, self.snapshoturi)
            triples = [
                    (uri, po.participant,
                        po.Participant+'#'+self.snapshotid+'-'+uid),
                    (uri, po.topic,
                        po.Topic+'#'+self.snapshotid+'-'+tid),
                    (uri, po.created, created),
            ]
            if updated != created:
                triples += [
                           (uri, po.updatedAt, updated),
                           ]
            count += 1
            if count % 60 == 0:
                c("finished supporters entries:", count, "ntriples:", len(triples))
                P.add(triples, self.translation_graph)
                c("finished add of supporters entries")
                triples = []
        if triples:
                P.add(triples, self.translation_graph)
        c("finished add of supporters entries")

    def translateLinks(self):
        for link in d['links']:
            lid=link[0]
            nome=link[1]
            url=link[2]
            tid=link[4]
            created=link[5]
            updated=link[6]
            uri = P.rdf.ic(po.Link,
                                self.snapshotid+"-"+str(lid),
                                self.translation_graph, self.snapshoturi)
            triples = [
                    (uri, po.name, nome),
                    (uri, po.url, url),
                    (uri, po.topic,
                        po.Topic+'#'+self.snapshotid+'-'+str(tid)),
                    uri, po.createdAt, created)
            ]
            if updated != created:
                triples += [
                           (uri, po.updatedAt, updated),
                           ]
            count += 1
            if count % 60 == 0:
                c("finished links entries:", count, "ntriples:", len(triples))
                P.add(triples, self.translation_graph)
                c("finished add of links entries")
                triples = []
        if triples:
                P.add(triples, self.translation_graph)
        c("finished add of links entries")
    def translateObservatories(self):
        =
        return
    def translateToRdf(self):
        pass
        self.translateUsers()
        self.translateUsers2()
        self.translateTopics()
        self.translateComments()
        self.translateCompetitions()
        self.translatePrizes()
        self.translateTags()
        self.translateTaggings()
        self.translateStates()
        self.translateCities()
        self.translateNeighborhoods()
        self.translatePlaces()
        self.translateSupporters()
        self.translateLinks()
        translateObservatories()
        pass

    def getData(self):
        db = MySQLdb.connect(user=cd.mysqluser, passwd=cd.mysqlpassword,
                             db=cd.mysqldb)  # , use_unicode=True)
        # db.query("SET NAMES utf8")
        # db.query('SET character_set_connection=utf8')
        # db.query('SET character_set_client=utf8')
        # db.query('SET character_set_results=utf8')
        db.query("show tables;")
        res = db.store_result()
        aa_tables = [res.fetch_row()[0][0] for i in range(res.num_rows())]
        d = {}
        for tt in aa_tables:
            # db.query("select column_name from information_schema.columns\
            #    where table_name='%s';"%(tt,))
            db.query("SHOW columns FROM %s;" % (tt,))
            res = db.store_result()
            d["h"+tt] = [res.fetch_row()[0][0] for i in range(res.num_rows())]
            db.query("select * from %s;" % (tt,))
            res = db.store_result()
            d[tt] = [res.fetch_row()[0] for i in range(res.num_rows())]
        self.data = d

if __name__ == '__main__':
    P.start(False)
    triplification_class = CidadeDemocraticaPublishing()
