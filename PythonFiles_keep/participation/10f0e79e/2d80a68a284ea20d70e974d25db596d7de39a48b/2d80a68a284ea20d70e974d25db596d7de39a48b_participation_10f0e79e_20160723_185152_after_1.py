import re
import os
import string
from validate_email import validate_email
import datetime
import MySQLdb
import percolation as P
from percolation.rdf import po, c, a
import participation as Pa
exec(open(Pa.PARTICIPATIONDIR+"accesses.py").read())


class CidadeDemocraticaPublishing:
    snapshotid = "cidadedemocratica-legacy"
    translation_graph = "cidadedemocratica_translation"
    meta_graph = "cidadedemocratica_meta"
    __ID = 0

    def __init__(self):
        self.snapshoturi = P.rdf.ic(po.Snapshot,
                                    self.snapshotid, self.translation_graph)
        c("get data")
        self.getData()
        c("start translate")
        self.translateToRdf()
        self.makeMeta()
        c("start render")
        self.writeRdf()
        c("finished render")

    def writeRdf(self):
        pub_dir = './cidadedemocratica_snapshot/'
        if not os.path.isdir(pub_dir):
            os.mkdir(pub_dir)
        # g = P.context(self.translation_graph)
        # g.serialize(pub_dir+'cidadedemocratica.ttl', 'turtle')
        # c('participation ttl serialized')
        # g.serialize(pub_dir+'cidadedemocratica.rdf', 'xml')
        # c('participation xml serialized')
        P.rdf.writeByChunks(pub_dir+'cidadedemocratica',
                            context=self.translation_graph,
                            ntriples=100000)
        # metadados: group, platform,
        g = P.context(self.meta_graph)
        g.serialize(pub_dir+'cidadedemocraticaMeta.ttl', 'turtle')
        c('participation meta ttl serialized')
        g.serialize(pub_dir+'cidadedemocraticaMeta.rdf', 'xml')
        c('participation meta xml serialized')

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
                 (self.snapshoturi, po.socialProtocol, 'Cidade Democrática'),
                 (self.snapshoturi, po.dateObtained, datetime.date(2014, 3, 19)),
                 ]
        P.add(triples, self.meta_graph)

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
            participanturi = po.Participant+'#'+self.snapshotid+"-"+str(uid)
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
                    (participanturi, po.selfDescription,
                     desc.replace('', '')),
                ]
            site = userd[5]
            if site:
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
                 "Problema": 'problem'}
        count = 0
        triples = []
        for topico in self.data['topicos']:
            tid = topico[0]
            ttype = topico[1]
            uid = topico[2]
            titulo = topico[3]
            desc = topico[4].replace('', '')
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
            participanturi = po.Participant+'#'+self.snapshotid+"-"+str(uid)
            topicuri = P.rdf.ic(po.Topic,
                                self.snapshotid+"-"+str(tid),
                                self.translation_graph, self.snapshoturi)
            triples += [
                (topicuri, po.author, participanturi),
                (topicuri, po.title, titulo),
                (topicuri, po.description, desc),
                (topicuri, po.createdAt, created),
                (topicuri, po.commentCount, ccomments),
                (topicuri, po.adhesionCount, cadesoes),
                (topicuri, po.relevance, relevancia),
                (topicuri, po.followersCount, cseguidores),
                (topicuri, po.topicType, trans[ttype]),
            ]
            if updated != created:
                 triples.append(
                    (topicuri, po.updatedAt, updated),
                 )
            if competition_id:
                assert isinstance(competition_id, int)
                competitionuri = po.Competition+'#'+self.snapshotid+"-"+str(competition_id)
                triples.append((topicuri, po.competition, competitionuri))
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
        triples = []
        count = 0
        for comment in self.data['comments']:
            cid = comment[0]
            tid = comment[1]  # topic id
            body = comment[3]
            if not body:
                continue
            body = body.replace('', '')
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
            participanturi = po.Participant+'#'+self.snapshotid+"-"+str(uid)
            # topicuri = self.topicuris[tid]
            topicuri = po.Topic+'#'+self.snapshotid+'-'+str(tid)
            triples += [
                (commenturi, po.author, participanturi),
                (commenturi, po.topic, topicuri),
                (commenturi, po.text, body),
                # (commenturi, po.nChars, len(body)),
                (commenturi, po.type, trans[ctype]),
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
        triples = []
        for competition in self.data['competitions']:
            coid = competition[0]
            sdesc = competition[1]
            created = competition[3]
            updated = competition[4]
            start = competition[5]
            title = competition[11]
            ldesc = competition[14]
            adesc = competition[15]
            reg = competition[16]
            aw = competition[17]
            part = competition[18]
            competitionuri = P.rdf.ic(po.Competition,
                                      self.snapshotid+"-"+str(coid),
                                      self.translation_graph, self.snapshoturi)
            triples += [
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
        if triples:
            P.add(triples, self.translation_graph)
        c("finisheg add of competitiok entries")

    def translatePrizes(self):
        count = 0
        triples = []
        for prize in self.data["competition_prizes"]:
            pid = prize[0]
            name = prize[1]
            description = prize[2]
            competition_id = prize[3]
            offerer_id = prize[4]
            tid = prize[5]
            created = prize[6]
            updated = prize[7]
            prizeuri = P.rdf.ic(po.Prize,
                                self.snapshotid+"-"+str(pid),
                                self.translation_graph, self.snapshoturi)

            triples += [
                    (prizeuri, po.name, name),
                    (prizeuri, po.description, description),
                    (prizeuri, po.description, description),
                    (prizeuri, po.competition,
                        po.Competition+"#"+self.snapshotid+'-'+str(competition_id)),
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
        triples = []
        for tag in self.data["tags"]:
            tid = tag[0]
            tag_ = tag[1]
            relevancia = tag[2]

            uri = P.rdf.ic(po.Tag,
                           self.snapshotid+"-"+str(tid),
                           self.translation_graph, self.snapshoturi)
            triples += [
                        (uri, po.text, tag_),
                        (uri, po.relevance, relevancia),
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
        triples = []
        for tagging in self.data["taggings"]:
            tid_ = tagging[0]
            tid = tagging[1]
            toid = tagging[2]
            uid = tagging[3]
            ttype = tagging[5]
            created = tagging[7]

            uri = po.Tagging+"#"+self.snapshotid+'-'+str(tid_)
            uri = P.rdf.ic(po.Tagging,
                           self.snapshotid+"-"+str(tid_),
                           self.translation_graph, self.snapshoturi)
            triples += [
                (uri, po.tag, po.Tag+"#"+self.snapshotid+'-'+str(tid)),
                (uri, po.tagger, po.Participant+"#"+self.snapshotid+'-'+str(uid)),
                (uri, po.createdAt, created)
            ]
            if ttype == "Topico":
                # tagging -> topico
                triples.append((uri, po.tagged,
                                po.Topic+'#'+self.snapshotid+'-'+str(toid)))
            else:
                triples.append((uri, po.tagged,
                                po.Macrotag+"#"+self.snapshotid+'-'+str(toid)))
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
        triples = []
        for estado in self.data["estados"]:
            gid = estado[0]
            nome = estado[1]
            abr = estado[2]
            created = estado[3]
            updated = estado[4]
            relevance = estado[5]
            uri = P.rdf.ic(po.State,
                           self.snapshotid+"-"+str(gid),
                           self.translation_graph, self.snapshoturi)
            triples += [
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
        count = 0
        triples = []
        for cidade in self.data["cidades"]:
            cid = cidade[0]
            nome = cidade[1]
            eid = cidade[2]
            slug = cidade[3]
            created = cidade[4]
            updated = cidade[5]
            relevance = cidade[6]
            uri = P.rdf.ic(po.City,
                           self.snapshotid+"-"+str(cid),
                           self.translation_graph, self.snapshoturi)
            triples += [
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
        triples = []
        for bairro in self.data["bairros"]:
            bid = bairro[0]
            nome = bairro[1]
            cid = bairro[2]
            created = bairro[3]
            updated = bairro[4]
            relevance = bairro[5]
            uri = P.rdf.ic(po.Neighborhood,
                           self.snapshotid+"-"+str(bid),
                           self.translation_graph, self.snapshoturi)
            triples += [
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
        triples = []
        for local in self.data["locais"]:
            lid = local[0]
            rid = local[1]
            rtype = local[2]
            bid = local[3]
            cid = local[4]
            created = local[7]
            updated = local[8]
            cep = local[9]
            eid = local[10]
            uri = P.rdf.ic(po.Place,
                           self.snapshotid+"-"+str(lid),
                           self.translation_graph, self.snapshoturi)
            triples += [(uri, po.createdAt, created)]
            if bid:
                triples.append((uri, po.neighborhood,
                                po.Neighborhood+'#'+self.snapshotid+'-'+str(bid)))
            if cid:
                triples.append((uri, po.city,
                                po.City+'#'+self.snapshotid+'-'+str(cid)))
            if eid:
                triples.append((uri, po.state,
                                po.State+'#'+self.snapshotid+'-'+str(eid)))
            if cep:
                triples.append((uri, po.cep, cep))
            if updated != created:
                triples += [
                           (uri, po.updatedAt, updated),
                           ]
            if rtype == "Topico":
                uri_ = po.Topic+'#'+self.snapshotid+'-'+str(rid)
            elif rtype == "User":
                uri_ = po.User+'#'+self.snapshotid+'-'+str(rid)
            elif rtype == "Competition":
                uri_ = po.Competition+'#'+self.snapshotid+'-'+str(rid)
            elif rtype == "Observatorio":
                uri_ = po.Observatory+'#'+self.snapshotid+'-'+str(rid)
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
        triples = []
        for adesao in self.data["adesoes"]:
            tid = adesao[0]
            uid = adesao[1]
            created = adesao[2]
            updated = adesao[3]
            aid = adesao[4]
            uri = P.rdf.ic(po.Support,
                           self.snapshotid+"-"+str(aid),
                           self.translation_graph, self.snapshoturi)
            triples += [
                    (uri, po.participant,
                        po.Participant+'#'+self.snapshotid+'-'+str(uid)),
                    (uri, po.topic,
                        po.Topic+'#'+self.snapshotid+'-'+str(tid)),
                    (uri, po.createdAt, created),
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
        count = 0
        triples = []
        for link in self.data['links']:
            lid = link[0]
            nome = link[1]
            url = link[2]
            tid = link[4]
            created = link[5]
            updated = link[6]
            uri = P.rdf.ic(po.Link,
                           self.snapshotid+"-"+str(lid),
                           self.translation_graph, self.snapshoturi)
            triples += [
                    (uri, po.name, nome),
                    (uri, po.url, url),
                    (uri, po.topic,
                        po.Topic+'#'+self.snapshotid+'-'+str(tid)),
                    (uri, po.createdAt, created)
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
        count = 0
        triples = []
        for observatorio in self.data["observatorios"]:
            oid = observatorio[0]
            uid = observatorio[1]
            created = observatorio[4]
            updated = observatorio[5]
            uri = P.rdf.ic(po.Observatory,
                           self.snapshotid+"-"+str(oid),
                           self.translation_graph, self.snapshoturi)
            triples += [
                    (uri, po.participant,
                        po.Participant+'#'+self.snapshoturi+'-'+str(uid)),
                    (uri, po.createdAt, created),
            ]
            if updated != created:
                triples += [
                           (uri, po.updatedAt, updated),
                           ]
            count += 1
            if count % 60 == 0:
                c("finished observatory  entries:", count, "ntriples:", len(triples))
                P.add(triples, self.translation_graph)
                c("finished add of observatory entries")
                triples = []
        if triples:
                P.add(triples, self.translation_graph)
        c("finished add of observatory entries")

    def translateObservatoryTags(self):
        triples = []
        for ot in self.data["observatorios_tem_tags"]:
            oid = ot[0]
            tid = ot[1]
            triples.append((po.Observatory+'#'+self.snapshotid+'-'+str(oid),
                            po.hasTag, po.Tag+'#'+self.snapshotid+'-'+str(tid)))
        P.add(triples, self.translation_graph)
        c("finished add of observatory tag entries")

    def translateLoginHistory(self):
        triples = []
        for login in self.data["historico_de_logins"]:
            lid = login[0]
            uid = login[1]
            created = login[2]
            ip = login[3]
            uri = P.rdf.ic(po.Login,
                           self.snapshotid+"-"+str(lid),
                           self.translation_graph, self.snapshoturi)
            triples += [
                    (uri, po.participant,
                        po.Participant+'#'+self.snapshotid+'-'+str(uid)),
                    (uri, po.createdAt, created),
                    (uri, po.ip, ip)
            ]
        P.add(triples, self.translation_graph)
        c("finished add of login entries")

    def translateInspirations(self):
        count = 0
        triples = []
        for inspiration in self.data["inspirations"]:
            iid = inspiration[0]
            cid = inspiration[1]
            desc = inspiration[2]
            created = inspiration[3]
            updated = inspiration[4]
            image = inspiration[5]
            uid = inspiration[6]
            title = inspiration[7]
            uri = P.rdf.ic(po.Inspiration,
                           self.snapshotid+"-"+str(iid),
                           self.translation_graph, self.snapshoturi)
            triples += [
                    (uri, po.competition,
                        po.Competition+'#'+self.snapshotid+'-'+str(cid)),
                    (uri, po.description, desc),
                    (uri, po.createdAt, created),
                    (uri, po.participant,
                        po.Participant+'#'+self.snapshotid+'-'+str(uid)),
                    (uri, po.title, title),
                    (uri, po.filename, image),
            ]
            if updated != created:
                triples += [
                           (uri, po.updatedAt, updated),
                           ]
            count += 1
            if count % 60 == 0:
                c("finished inspiration entries:", count, "ntriples:", len(triples))
                P.add(triples, self.translation_graph)
                c("finished add of inspiration entries")
                triples = []
        if triples:
                P.add(triples, self.translation_graph)
        c("finished add of inspiration entries")

    def translateImages(self):
        triples = []
        count = 0
        for imagem in self.data["imagens"]:
            iid = imagem[0]
            rid = imagem[1]
            rtype = imagem[2]
            size = imagem[3]
            ctype = imagem[4]
            fname = imagem[5]
            height = imagem[6]
            width = imagem[7]
            legenda = imagem[11]
            created = imagem[12]
            updated = imagem[13]
            uri = P.rdf.ic(po.Image,
                           self.snapshotid+"-"+str(iid),
                           self.translation_graph, self.snapshoturi)
            triples.append((uri, po.createdAt, created))
            if rtype == "User":
                triples.append((uri, po.accountable,
                                po.Participant+"#"+self.snapshotid+'-'+str(rid)))
            if rtype == "Topico":
                triples.append((uri, po.accountable,
                                po.Topic+"#"+self.snapshotid+'-'+str(rid)))
            if size:
                triples.append((uri, po.size, int(size)))
            if ctype:
                triples.append((uri, po.contentType, ctype))
            if fname:
                triples.append((uri, po.filename, fname))
            if height:
                triples.append((uri, po.height, int(height)))
            if width:
                triples.append((uri, po.width, int(width)))
            if legenda:
                triples.append((uri, po.caption, legenda))
            if updated != created:
                triples.append((uri, po.updatedAt, updated))
            count += 1
            if count % 60 == 0:
                c("finished image  entries:", count, "ntriples:", len(triples))
                P.add(triples, self.translation_graph)
                c("finished add of image entries")
                triples = []
        if triples:
                P.add(triples, self.translation_graph)
        c("finished add of prizes entries")

    def translateMacrotags(self):
        triples = []
        for mt in self.data["macro_tags"]:
            mtid = mt[0]
            title = mt[1]
            created = mt[2]
            updated = mt[3]
            uri = P.rdf.ic(po.Macrotag,
                           self.snapshotid+"-"+str(mtid),
                           self.translation_graph, self.snapshoturi)
            triples.append((uri, po.createdAt, created))
            if updated != created:
                triples += [
                           (uri, po.updatedAt, updated),
                           ]
            if title:
                triples.append((uri, po.title, title))
        P.add(triples, self.translation_graph)
        c("finished add of microtag entries")

    def translateToRdf(self):
        self.translateUsers()
        self.translateUsers2()
        self.translateTopics()
        self.translateComments()
        self.translateCompetitions()
        self.translatePrizes()
        # self.translateTags()
        # self.translateTaggings()
        self.translateStates()
        self.translateCities()
        self.translateNeighborhoods()
        self.translatePlaces()
        self.translateSupporters()
        # self.translateLinks()
        self.translateObservatories()
        # self.translateObservatoryTags()
        # self.translateLoginHistory()
        self.translateInspirations()
        # self.translateImages()
        # self.translateMacrotags()

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
