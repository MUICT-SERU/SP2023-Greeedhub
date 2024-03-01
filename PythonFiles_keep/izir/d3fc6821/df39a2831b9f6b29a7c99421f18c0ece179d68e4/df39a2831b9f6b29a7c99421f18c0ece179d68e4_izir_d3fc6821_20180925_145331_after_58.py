from pymongo import MongoClient
import izi


client = MongoClient('db', 27017)
db = client['our-database']
collection = db['our-items']


@izi.get('/', output=izi.output_format.pretty_json)
def show():
    """Returns a list of items currently in the database"""
    items = list(collection.find())
    # JSON conversion chokes on the _id objects, so we convert
    # them to strings here
    for i in items:
        i['_id'] = str(i['_id'])
    return items


@izi.post('/new', status_code=izi.falcon.HTTP_201)
def new(name: izi.types.text, description: izi.types.text):
    """Inserts the given object as a new item in the database.

    Returns the ID of the newly created item.
    """
    item_doc = {'name': name, 'description': description}
    collection.insert_one(item_doc)
    return str(item_doc['_id'])

