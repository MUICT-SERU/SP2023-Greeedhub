#coding=utf8
import re, json, time
from plugin.Sqlite3Client import Sqlite3Client

VOTE_KEYWORD = 'vote'

def load_vote_list():
    try:
        with open('vote.json') as f: voteList = json.loads(f.read())
        if not voteList: raise Exception
        for voteItem in voteList: # test json format
            if not (voteItem.has_key('name') and voteItem.has_key('candidates')): raise Exception
            if not (isinstance(voteItem['candidates'], list) and voteItem['candidates']): raise Exception
        return voteList
    except:
        print 'There is something wrong with vote.json'

def get_status(storageClass, userName):
    r = storageClass.get_other(userName)
    return storageClass.get_dict_of_other(r)

def store_status(storageClass, userName, other):
    PYQuanPin = storageClass.find_PYQuanPin(userName)
    storageClass.update_user(PYQuanPin, Other = storageClass.get_str_of_other(other))

def vote(storageClass, userName, msg):
    if not VOTE_KEYWORD in msg: return False
    # key in sqlite3->other: vote
    # value in sqlite3->other: -1 for voted, 0 for waiting for vote, 1 for not voted
    # values should be strings
    voteList = load_vote_list()
    if voteList is None: return False
    status = get_status(storageClass, userName)
    for voteItem in voteList:
        if not voteItem['name'] in msg: continue
        if status.has_key('vote@' + voteItem['name']) and status['vote@' + voteItem['name']] == '-1':
            return 'You have voted in ' + voteItem['name']
        candidate = None
        for c in voteItem['candidates']:
            # bug will occur if one candidates's name contains another's
            if c in msg: candidate = c;break
        if candidate is None: return 'Candidates contains: ' + ', '.join(voteItem['candidates'])
        # update vote database
        with Sqlite3Client(storageClass.sqlDir) as s3c:
            s3c.execute('create table if not exists vote (name text, candidate text, PYQuanPin text, time text)')
            PYQuanPin = storageClass.find_PYQuanPin(userName)
            s3c.insert_data('vote', items = [voteItem['name'], candidate, PYQuanPin, int(time.time())])
        # update user status
        status['vote@' + voteItem['name']] = '-1'
        store_status(storageClass, userName, status)
        return 'Vote for %s successfully'%candidate
        break
    return 'There are votes going on: ' + ', '.join([voteItem['name'] for voteItem in voteList])
