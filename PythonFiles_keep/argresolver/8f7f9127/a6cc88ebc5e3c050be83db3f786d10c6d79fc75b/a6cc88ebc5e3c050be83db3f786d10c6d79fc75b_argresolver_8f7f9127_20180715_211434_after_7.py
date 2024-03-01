# We inject arguments from the environment variables scope to a simple function
# We use a `prefix` to minimize clashes with other components
# username will have a correponding DB_USERNAME, same for password and database

from argresolver import Environment
from argresolver.utils import modified_environ  # We use it to alter the environment variables

@Environment()
def connect(host, user, password):
    print("Connecting: {user}:{password}@{host}".format(**locals()))

with modified_environ(PASSWORD='my_pass'):
    connect('localhost', 'admin')
# Prints: Connecting: admin:my_pass@localhost