import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'test_suite.settings'
import sys 
import django
from distutils.version import LooseVersion
from django.test.utils import get_runner
from django.conf import settings


if LooseVersion(django.get_version()) >= LooseVersion('1.7'):
    django.setup()

TestRunner = get_runner(settings)
test_runner = TestRunner(verbosity=1, interactive=True, failfast=True)
failures = test_runner.run_tests(['test_suite',])
sys.exit(failures)

