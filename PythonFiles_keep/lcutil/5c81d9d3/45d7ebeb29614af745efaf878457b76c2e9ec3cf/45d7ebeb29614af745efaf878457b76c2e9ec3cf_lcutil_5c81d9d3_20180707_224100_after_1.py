""" General database functions.

    Should work with DB API 2.0 cursors, tested with psycopg2.
    https://www.python.org/dev/peps/pep-0249/
"""

def as_dicts(cursor):
    """ Return a list of dictionaries from a result-set.
    """
    fields = [k[0] for k in cursor.description]
    result = []
    rows = cursor.fetchall()
    for row in rows:
        result.append(dict(zip(fields, row)))

    return(result)


def dict_iter(cursor):
    """ A generator of result-set dictionaries.

        Use this function when the result-set don't fit into memory.
    """
    fields = [k[0] for k in cursor.description]
    row = cursor.fetchone()
    while row:
        yield dict(zip(fields, row))
        row = cursor.fetchone()


def insert_record(cursor, table, record):
    """ Insert a given record into the table specified.

        cursor.commit() should be preformed outside this function.
    """
    fields = ', '.join(record.keys())
    values = ', '.join(['%%(%s)s' % field for field in record.keys()])
    sql = "INSERT into %s (%s) VALUES (%s);" % (table, fields, values)

    cursor.execute(sql, record)
