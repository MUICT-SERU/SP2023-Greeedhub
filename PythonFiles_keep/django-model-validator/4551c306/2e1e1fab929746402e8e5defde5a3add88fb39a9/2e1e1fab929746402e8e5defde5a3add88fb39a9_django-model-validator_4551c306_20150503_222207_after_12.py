import os
PROJECT_DIR = os.path.dirname(__file__)

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE':   'django.db.backends.sqlite3',
        'NAME':     '/tmp/playground.db',
    }
}

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',

    'test_suite',
)
MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

SECRET_KEY = 'asd6asdf7b1esdfasd0fasdfbf0690dsdfas0df9sdf2sd9f16254fgjdf47ed1741c'

