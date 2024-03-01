import rdflib as r
import urllib
import datetime
import re
import codecs
import rfc3986
import percolation as P
from percolation.rdf import po, a, c
from percolation.rdf.publishing import TranslationPublishing
import babel
from validate_email import validate_email
from bs4 import BeautifulSoup


class DataTable:
    def __init__(self, data_values, column_names):
        """data_values: iterable of iterables,
        column_names: iterable"""
        locals_ = locals().copy()
        del locals_["self"]
        for i in locals_:
            exec("self.{}={}".format(i, i))

    def get(self, column_name):
        index = self.column_names.index(column_name)
        return [i[index] for i in self.data_values]

    def getMany(self, column_names):
        indexes = [self.column_names.index(i) for i in column_names]
        return [[i[index] for index in indexes] for i in self.data_values]


class ParticipabrPublishing(TranslationPublishing):
    snapshotid = "participabr-legacy"
    translation_graph = "participabr-translation"
    meta_graph = "participabr-meta"

    def __init__(self, postgresql_cursor):
        snapshoturi = P.rdf.ic(po.ParticipabrSnapshot,
                               self.snapshotid, self.translation_graph)
        P.add((snapshoturi, a, po.Snapshot), context=self.translation_graph)
        cur = postgresql_cursor
        datas2 = []
        datas = []
        bodies = []
        locals_ = locals().copy()
        del locals_["self"]
        for i in locals_:
            exec("self.{}={}".format(i, i))
        c("get data")
        self.getData(cur)
        c("start translate")
        self.translateToRdf()

    def translateProfiles(self):
        triples = []
        count = 0
        for identifier, name, type_, visible, public_profile,\
            lat, lng, created_at, updated_at, data, id_\
            in self.profiles_table.getMany(
              ["identifier", "name", "type", "visible", "public_profile", "lat",
               "lng", "created_at", "updated_at", "data", "id"]):
            assert identifier.islower() or identifier.isdigit()
            participanturi = P.rdf.ic(po.Participant,
                                      self.snapshotid+"-"+identifier,
                                      self.translation_graph, self.snapshoturi)
            profileuri = P.rdf.ic(po.Profile,
                                  self.snapshotid+"-"+str(id_),
                                  self.translation_graph,
                                  self.snapshoturi)
            # c(identifier)
            assert bool(name)
            assert type_ in ("Person", "Community", "Enterprise")
            assert visible in (False, True)
            assert public_profile in (False, True)
            assert isinstance(created_at, datetime.datetime)
            assert isinstance(updated_at, datetime.datetime)
            triples = [
                      (participanturi, po.name, name),
                      (participanturi, a, eval("po."+type_)),
                      (participanturi, po.profile, profileuri),
                      (profileuri, po.visible, visible),
                      (profileuri, po.public, public_profile),
                      (profileuri, po.createdAt, created_at),
                      (profileuri, po.updatedAt, updated_at),
                      ]
            assert isinstance(lat, (type(None), float))
            assert isinstance(lng, (type(None), float))
            assert type(lat) == type(lng)
            if lat:
                place = r.BNode()
                triples += [
                           (participanturi, po.basedNear, place),
                           (place, po.latitude, lat),
                           (place, po.longitude, lng),
                           ]
            data_, triples_ = parseData(data, participanturi)
            triples += triples_
            for field in data_:
                triples += [
                           (participanturi, eval("po."+field), data_[field])
                           ]
            self.datas += [(data_, data)]
            email = self.emails.get(identifier)
            if email:
                assert validate_email(email)
                triples += [
                           (participanturi, po.email, email),
                           ]
            count += 1
            if count % 1 == 0:
                c("profiles done:", count)
                break
        c("finished triplification of profiles")
        P.add(triples, self.translation_graph)
        c("finished add of profiles to endpoint")

    def translateArticles(self):
        triples = []
        count=0
        for profile_id, published, id_, type_, body, abstract, created_at,\
                updated_at, published_at, hits, start_date, end_date,\
                parent_id, position, path, setting in\
                self.articles_table.getMany(
                    ("profile_id", "published", "id",
                     "type", "body", "abstract", "created_at", "updated_at",
                     "published_at", "hits", "start_date", "end_date",
                     "parent_id", "position", "path", "setting")
                ):
            identifier = self.profileids[profile_id]
            participanturi = po.Participant+"#"+self.snapshotid+"-"+identifier
            type__ = type_.split("::")[-1]
            articleuri = P.rdf.ic(eval("po."+type__),
                                  self.snapshotid+"-"+str(id_),
                                  self.translation_graph, self.snapshoturi)
            assert isinstance(created_at, datetime.datetime)
            assert isinstance(updated_at, datetime.datetime)
            assert isinstance(published_at, datetime.datetime)
            triples += [
                       (articleuri, a, po.Article),
                       (articleuri, po.author, participanturi),
                       (articleuri, po.createdAt, created_at),
                       (articleuri, po.updatedAt, updated_at),
                       (articleuri, po.publishedAt, published_at),
                       (articleuri, po.published, published),
                       (articleuri, po.hits, hits),
                       (articleuri, po.path, path),
                       ]
            if not body or body.startswith("---") or \
                    body == '<p>artigo filho</p>' or \
                    body.strip().count(" ") < 2:
                body = ""
            if body:
                if re.findall(r"<(.*)>(.*)<(.*)>", body, re.S):
                    rawbody = BeautifulSoup(body, 'html.parser').get_text()
                    triples += [
                               (articleuri, po.htmlBodyText, body),
                               (articleuri, po.cleanBodyText, rawbody),
                               ]
                else:
                    triples += [
                               (articleuri, po.cleanBodyText, body),
                               ]
                self.bodies += [body]
            if abstract:
                if re.findall(r"<(.*)>(.*)<(.*)>", abstract, re.S):
                    rawbody = BeautifulSoup(abstract, 'html.parser').get_text()
                    triples += [
                               (articleuri, po.htmlAbstractText, body),
                               (articleuri, po.cleanAbstractText, rawbody),
                               ]
                else:
                    triples += [
                               (articleuri, po.cleanAbstractText, body),
                               ]
            if parent_id:
                type2__ = self.articletypes[parent_id].split("::")[-1]
                articleuri2 = P.rdf.ic(eval("po."+type2__),
                                       self.snapshotid+"-"+str(parent_id),
                                       self.translation_graph, self.snapshoturi)
                triples += [
                           (articleuri, po.parent, articleuri2),
                           ]
                if type__ == "Step":
                    assert isinstance(position, int)
                    triples += [
                               (articleuri, po.stepOf, articleuri2),
                               (articleuri, po.position, position),
                               ]
                elif type__ == "Mediation":
                    triples += [
                               (articleuri, po.mediationOf, articleuri2),
                               ]
            if start_date:
                assert isinstance(start_date, datetime.date)
                triples += [
                           (articleuri, po.startAt, start_date),
                           ]
            if end_date:
                assert isinstance(end_date, datetime.date)
                triples += [
                           (articleuri, po.endAt, end_date),
                           ]
            if setting:
                data2_, triples2_ = parseData(setting, articleuri)
                triples += triples2_
                self.datas2 += [(data2_, setting)]
            count += 1
            if count % 1 == 0:
                c("articles done:", count)
                break
        c("finished triplification of articles")
        P.add(triples, self.translation_graph)
        c("finished add of articles")

    def translateComments(self):
        triples = []
        count = 0
        for id_, title, body, created_at, source_id, reply_of_id, ip_address,\
            author_id, referrer in self.comments_table.getMany(
                ("id", "title", "body", "created_at", "source_id",
                 "reply_of_id", "ip_address", "author_id", "referrer")):
            if title and title.startswith("Teste de Stress"):
                continue
            if body.count(body[0]) == len(body) or\
                    body.lower() in ("teste", "testee", "teste 2", "texte abc")\
                    or "participabr teste" in body or\
                    (len(set(body.lower())) < 3 and len(body) > 2):
                continue
            commenturi = P.rdf.ic(
                po.Comment, self.snapshotid+"-"+str(id_),
                self.translation_graph, self.snapshoturi)
            assert isinstance(created_at, datetime.datetime)
            assert isinstance(body, str) and not re.findall(r"<.*>.*<.*>", body)
            assert isinstance(source_id, int)
            if source_id not in self.articletypes:
                articleclass = po.Article
            else:
                articleclass = eval(
                    "po."+self.articletypes[source_id].split("::")[-1])
            articleuri = P.rdf.ic(
                articleclass, self.snapshotid+"-"+str(source_id),
                self.translation_graph, self.snapshoturi)
            triples += [
                       (commenturi, po.createdAt, created_at),
                       (commenturi, po.bodyText, body),
                       (commenturi, po.sourceArticle, articleuri),
                       ]
            if title and len(title) > 2 and title.count(title[0]) != len(title)\
                    and not title.startswith("hub-message"):
                triples += [
                           (commenturi, po.title, title)
                           ]
            if reply_of_id:
                assert isinstance(reply_of_id, int)
                commenturi0 =\
                    po.Comment+"#"+self.snapshotid+"-"+str(reply_of_id)
                triples += [
                           (commenturi, po.replyOf, commenturi0)
                           ]
            if ip_address:
                triples += [
                           (commenturi, po.ipAddress, ip_address)
                           ]
            if author_id and author_id in self.userids:
                participanturi =\
                  po.Participant+"#"+self.snapshotid+"-"+self.userids[author_id]
                triples += [
                           (commenturi, po.author, participanturi)
                           ]
            if referrer:
                assert rfc3986.is_valid_uri(referrer)
                triples += [
                           (commenturi, po.url, referrer)
                           ]
            count += 1
            if count % 1 == 0:
                c("done:", count)
                break
        c("finished triplification of comments")
        P.add(triples, self.translation_graph)
        c("finished add of comments")

    def translateFriendships(self):
        triples = []
        fids = self.friendships_table.getMany(("person_id", "friend_id"))
        added_friendships = []
        count=0
        for person_id, friend_id, created_at, group in \
                self.friendships_table.getMany(
                    ('person_id', 'friend_id', 'created_at', 'group')):
            if [friend_id, person_id] in added_friendships:
                pass
            else:
                added_friendships += [[person_id, friend_id]]
            id0 = self.profileids[person_id]
            id1 = self.profileids[friend_id]
            friendshipuri = P.rdf.ic(po.Friendship,
                                     self.snapshotid+'-'+id0+'-'+id1,
                                     self.translation_graph, self.snapshoturi)
            participanturi0 = po.Participant+"#"+self.snapshotid+"-"+id0
            participanturi1 = po.Participant+"#"+self.snapshotid+"-"+id1
            assert isinstance(created_at, datetime.datetime)
            triples += [
                       (friendshipuri, po.member, participanturi0),
                       (friendshipuri, po.member, participanturi1),
                       (friendshipuri, po.createdAt, created_at),
                       ]
            if [friend_id, person_id] not in fids:
                triples += [
                           (participanturi0, po.knows, participanturi1),
                           ]
            if group:
                triples += [
                           (friendshipuri, po.socialCircle, group),
                           ]
            count += 1
            if count % 1 == 0:
                c("friendships done:", count)
                break
        c("finished triplification of friendships")
        P.add(triples, self.translation_graph)
        c("finished add of friendships")

    def translateVotes(self):
        triples = []
        commentids = set(self.comments_table.get("id"))
        count=0
        for id_, vote, voteable_id, voteable_type,\
            voter_id, voter_type, created_at in \
            self.votes_table.getMany(
                    ("id", "vote", "voteable_id",
                     "voteable_type", "voter_id", "voter_type", "created_at")):
            assert isinstance(id_, int)
            assert isinstance(voteable_id, int)
            assert isinstance(created_at, datetime.datetime)
            voteuri = P.rdf.ic(po.Vote, self.snapshotid+"-"+str(id_),
                               self.translation_graph, self.snapshoturi)
            if voteable_type == "Article":
                type__ = self.articletypes[voteable_id].split("::")[-1]
                referenceuri = \
                    eval("po."+type__)+"#"+self.snapshotid+"-"+str(voteable_id)
            elif voteable_type == "Comment":
                assert voteable_id in commentids
                referenceuri = \
                    po.Comment+"#"+self.snapshotid+"-"+str(voteable_id)
            else:
                raise ValueError("unexpected voteable type")
            triples += [
                       (voteuri, po.createdAt, created_at),
                       (voteuri, po.vote, vote),
                       (voteuri, po.reference, referenceuri),
                       ]
            if voter_id:
                assert voter_type == "Profile"
                assert isinstance(voter_id, int)
                participanturi = po.Participant + '#' + \
                    self.snapshotid+"-"+self.profileids[voter_id]
                triples += [
                           (voteuri, po.author, participanturi),
                           ]
            count += 1
            if count % 1 == 0:
                c("votes done:", count)
                break
        c("finished triplification of votes")
        P.add(triples, self.translation_graph)
        c("finished add of votes")

    def translateTagsTagging(self):
        triples = []
        count = 0
        for id_, name, parent_id, pending in self.tags_table.getMany(
                 ("id", "name", "parent_id", "pending")):
            assert isinstance(name, str)
            assert isinstance(id_, int)
            assert parent_id is None
            assert pending is False
            taguri = P.rdf.ic(po.Tag, self.snapshotid+"-"+str(id_),
                              self.translation_graph, self.snapshoturi)
            triples += [
                       (taguri, po.name, name)
                       ]
            count += 1
            if count % 1 == 0:
                c("taggings done:", count)
                break
        tagids = self.tags_table.get("id")
        count = 0
        for id_, tag_id, taggable_id, taggable_type, created_at in\
                self.taggings_table.getMany(
                    ('id', 'tag_id', 'taggable_id',
                     'taggable_type', 'created_at')):
            assert isinstance(id_, int)
            assert tag_id in tagids
            assert isinstance(taggable_id, int)
            assert isinstance(created_at, datetime.datetime)
            assert taggable_type == "Article"
            tagginguri = P.rdf.ic(po.Tagging, self.snapshotid+"-"+str(id_),
                                  self.translation_graph, self.snapshoturi)
            taguri = po.Tag+"#"+self.snapshotid+"-"+str(tag_id)
            type__ = self.articletypes[taggable_id].split("::")[-1]
            articleuri =\
                eval("po."+type__)+"#"+self.snapshotid+"-"+str(taggable_id)
            triples += [
                       (tagginguri, po.tag, taguri),
                       (tagginguri, po.article, articleuri),
                       (tagginguri, po.createdAt, created_at),
                       ]
            count += 1
            if count % 1 == 0:
                c("taggings done:", count)
                break
        P.add(triples, self.translation_graph)

    def translateToRdf(self):
        c("start profiles")
        self.translateProfiles()
        c("end profiles")
        self.translateArticles()
        c("end articles")
        self.translateComments()
        c("end comments")
        self.translateFriendships()
        c("end friendships")
        self.translateVotes()
        c("end votes")
        self.translateTagsTagging()
        c("end tags and tagging")
        # check 'pairwise_plugin_choices_related','units","inputs","tasks"

    def getData(self, cur):
        tables = ("users", 'profiles', 'articles', 'comments', 'friendships',
                  'votes', 'tags', 'taggings', "votes",
                  'pairwise_plugin_choices_related', 'units', "inputs", "tasks")
        for table in tables:
            # eval("{},{},{}=table_values,table_names,table_object")
            cur.execute('SELECT * FROM '+table)
            exec("{}_values=cur.fetchall()".format(table))
            cur.execute("select column_name from information_schema.columns\
                        where table_name='{}';".format(table))
            exec("{}_names=[i[0] for i in cur.fetchall()[::-1]]".format(table))
            exec("{}_table=DataTable({},{})".format(
                table, table+"_values", table+"_names"))
        emails = dict(locals()["users_table"].getMany(("login", "email")))
        profileids = dict(locals()["profiles_table"].getMany(
            ("id", "identifier")))
        articletypes = dict(locals()["articles_table"].getMany(("id", "type")))
        userids = dict(locals()["users_table"].getMany(("id", "login")))

        # ??? WHY WONT THIS WORK?? TTM
        # emails=users_table.getMany(("email","login"))
        locals_ = locals().copy()
        del locals_["self"]
        for i in locals_:
            exec("self.{}={}".format(i, i))


def fparse(mstring):
    foo = [i for i in mstring.split("\n")[1:-1] if i]
    return dict([[j.strip().replace('"', "") for j in i.split(":")[1:]]
                 for i in foo if len(i.split(":")) == 3])
U = r.URIRef
QQ = urllib.parse.quote


datafields = {'acronym',
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


def parseData(datastring, participanturi, setting=False):
    # candidates=datastring.split("\n")
    datastring = codecs.decode(datastring,
                               "unicode_escape").encode("latin1").decode("utf8")
    countries = babel.Locale("pt").territories
    # candidates = re.findall(r":(.*?): (.*)", datastring, re.S)
    candidates = re.findall(r":(.*?): (.*?)[:\n]", datastring, re.S)
    data = {}
    allowed = {"acronym", "contactEmail", "description",
               "organizationWebsite", "professionalActivity"}
#    process = {"addressReference",   # remove "não tem" and
#                                     # all([i.lower() =  = "x" for i in ar])
#            'allowUnauthenticatedComments', # bool(i)
#            'city',    # all([i.lower()=="-" for i in ar])
#            "country", # babel.Locale("pt").territories
#            "district",
#            "organization",
#            "state",
#            "tagList"}
#    removed = {"closed", "enableContactUs", "fieldsPrivacy",
#               "lastNotification", "layoutTemplate", "moderatedArticles",
#               "notificationTime", "subOrganizationsPluginParentToBe"}
    triples = []
    for field, value in candidates:
        if value and field:
            if re.findall(r":"+field+r": \"", datastring):
                # field value in quotes:
                value = re.findall(r":"+field+r': \"(.*?)\".*(?:$|:.*:.*)',
                                   datastring, re.S)[0]
            value.strip()
            if not value.replace("\"", ""):
                continue
            value_ = value
            field_ = re.sub(r"_(.)", lambda m: m.groups()[0].upper(), field)
#            assert field_ in datafields
            if field_ in allowed:
                pass
            elif field_ == "addressReference" and \
                           (value_ == "não tem" or
                            value_.count("x") == len(value_)):
                continue
            elif field_ == "zipCode" and \
                           (len(value_) == 1 or value_ == "não tem"):
                continue
            elif field_ == "tagList":
                field_ = "subjectMatter"
            elif field_ == "state" and "binary" in value_:
                continue
            elif field_ == "allowUnauthenticatedComments":
                value_ = bool(value_)
            elif field_ == "organization" and \
                           (value_.count("-") == len(value_) or
                            value_.count("0") == len(value_) or
                            value_.count(".") == len(value_) or
                            value_.count("*") == len(value_) or
                            value_.count("?") == len(value_) or
                            "binary" in value_ or "não tem" == value_):
                continue
            elif field_ == "district" and (value_.count("-") == len(value_) or
                                           "binary" in value_ or
                                           "não tem" == value_):
                continue
            elif field_ == "city" and (value_.count("-") == len(value_)):
                continue
            elif field_ == "country":
                if value_ in countries:
                    value_ = countries[value_]
                elif value_.title() in countries.values():
                    value_ = value.title()
                elif "binary" in value_:
                    continue
                elif 'Av. Deodoro da Fonseca' == value_:
                    continue
                elif 'Usa' == value_:
                    value_ = countries["US"]
                elif 'Países Baixos' in value_:
                    value_ = "Holanda"
                elif '/' in value_:
                    countries = value_.split("/")
                    for country in countries:
                        triples += [
                                   (participanturi, po.country, country),
                                   ]
            if setting:
                fields = {"visualizationFormat", "twitterConsumerKey",
                          "postsPerPage", "displayHits",
                          "twitterConsumerSecret",
                          "displayPostsInCurrentLanguage", "twitterAccessToken",
                          "twitterAccessTokenSecret", "publishSubmissions",
                          "followers", "displayVersions"}
                if field_ in fields:
                    continue
                elif field_ == "hashtagsTwitter":
                    field_ = "twitterHashtags"
                if field_ == "twitterHashtags":
                    hashtags = value_.split(",")
                    for hashtag in hashtags:
                        triples += [(participanturi, po.hashtag,
                                     hashtag.strip()), ]
                    continue
            if value_ in ('true', 'false'):
                value_ = (False, True)[value_ == 'true']
            triples += [
                       (participanturi, eval("po."+field_), value_),
                       ]
            data[field_] = value_
    return data, triples
