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
    snapshotid = "cidadedemocratica_legacy"
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
            uid=user[0]
            assert isinstance(uid, int)
            email=user[3]
            created=user[6]
            updated=user[7]
            type_=user[14]
            condition=user[12]
            try:
                assert validate_email(email)
            except AssertionError:
                email = re.sub(r"[;:,]","",email)
                email = email.replace("..",".").replace(".@","@").replace(
                    ".com.",".com.br").replace(".brbr",".br").replace(
                        "gmail.facebook.com.br.", "gmail.com").replace("@.","@")
                try:
                    assert validate_email(email)
                except AssertionError:
                    email = "".join(i for i in email if i in string.printable)
                    assert validate_email(email)
            assert isinstance(created,datetime.datetime)
            assert isinstance(updated,datetime.datetime)
            assert isinstance(condition, str)
            assert isinstance(type_, str)
            participanturi = P.rdf.ic(po.Participant,
                                      self.snapshotid+"-"+str(uid),
                                      self.translation_graph, self.snapshoturi)
            triples += [
                       (participanturi,po.email,email),
                       (participanturi,po.createdAt,created),
                       (participanturi,po.participantType,type_),
                       (participanturi,po.profileCondition,condition),
                       ]
            if updated != created:
                triples += [
                           (participanturi, po.updatedAt, updated),
                           ]
            deleted=user[13]
            if deleted:
                assert isinstance(deleted,datetime.datetime)
                triples += [
                           (participanturi, po.deletedAt, deleted),
                           ]
            relevance=user[20]
            if relevance:
                assert isinstance(relevance, int)
                triples += [
                           (participanturi, po.relevance, relevance),
                           ]
            insp_count=user[30]
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
        count = 0
        triples = []
        for userd in self.data["user_dados"]:
            uid = userd[1]
            nome = userd[2]
            # email=userd[4] priorizado o email da tabela users
            gender = userd[7]
            created = userd[10]
            updated = userd[11]
            assert isinstance(uid, int)
            assert isinstance(nome, str)
            assert isinstance(gender,str) and len(gender) == 1
            assert isinstance(created,datetime.datetime)
            assert isinstance(updated,datetime.datetime)
            participanturi = P.rdf.ic(po.Participant,
                                      self.snapshotid+"-"+str(uid),
                                      self.translation_graph, self.snapshoturi)
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
                assert isinstance(desc,str)
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
            fax = userd[9]
            assert isinstance(fax,str)
            uri=ocdp+"#"+uid
            g.add((uri,ocd.name,r.Literal(nome)))
            g.add((uri,ocd.phone,r.Literal(fone)))
        #    try:
        #        if du[uid][0]!=email:
        #            print "diferente"
        #            print "1: %s, 2: %s"%(du[uid][0],email)
        #    except:
        #        print "usuario existe no user_dados mas nao no users"
        #        foo.append(uid)
            g.add((uri,ocd.site,r.Literal(site)))
            g.add((uri,ocd.autoDescription,r.Literal(RCC(desc))))
            g.add((uri,ocd.gender,r.Literal(gen)))
            if ani:
                g.add((uri,ocd.birthday,r.Literal(parse(ani))))
            g.add((uri,ocd.fax,r.Literal(fax)))


    def translateToRdf(self):
        self.translateUsers()
        self.translateUsers2()
        pass

    def getData(self):
        db = MySQLdb.connect(user=cd.mysqluser, passwd=cd.mysqlpassword,
                             db=cd.mysqldb)# , use_unicode=True)
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
        self.data=d

if __name__ == '__main__':
    P.start(False)
    triplification_class = CidadeDemocraticaPublishing()
