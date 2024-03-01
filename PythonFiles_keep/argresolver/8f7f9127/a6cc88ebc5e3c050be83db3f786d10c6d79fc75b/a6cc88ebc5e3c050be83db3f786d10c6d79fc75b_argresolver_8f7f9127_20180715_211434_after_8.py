# We inject arguments from the environment variables scope 
# to an instance __init__.
# We use a `prefix` to minimize clashes with other components that have a username / password.
# Argument username will have a correponding DB_USERNAME, same for password and database

from argresolver import Environment
from argresolver.utils import modified_environ  # We use it to alter the environment variables

class Connection:
    @Environment(prefix='DB')
    def __init__(self, username, password, database='default'):
        self.username = username
        self.password = password
        self.database = database

    def __str__(self):
        # Hint: In a real world example you won't put your password in here ;-)
        return "Connection(username='{self.username}', password='{self.password}'"\
        ", database='{self.database}')".format(self=self)

with modified_environ(DB_USERNAME='admin', DB_PASSWORD='secret'):
    conn = Connection()
print(str(conn))  # Connection(username='admin', password='secret', database='default')