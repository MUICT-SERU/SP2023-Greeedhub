import datetime
import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from paramiko import SSHClient, AutoAddPolicy


class Command(BaseCommand):
    """
    This command will create Django models by introspecting the PostgreSQL data.
    Why not use inspectdb? It doesn't have enough options; this will be broken
    down by schema / product.
    """
    help = 'This command will copy the database from one environment to another. BE CAREFUL!'

    def add_arguments(self, parser):
        parser.add_argument(
            '--instance',
            action='store',
            dest='instance',
            default=None,
            help='''The instance from DJANGO_PUBLISHER_INSTANCES to publish.'''
        )
        parser.add_argument(
            '--quiet',
            action='store',
            dest='quiet',
            default=False,
            help='''Shuts off not quiet output.'''
        )
        parser.add_argument(
            '--stamp',
            action='store',
            dest='stamp',
            default='{0:%Y-%m-%d-%H-%M-%S}'.format(datetime.datetime.now()),
            help='''Shuts off not quiet output.'''
        )

    def command_output(self, stdout, stderr, quiet):
        """
        Dumps the output of the SSH command run via paramiko and
        error, if applicable.

        Output the errors, even in quiet mode.
        """
        if not quiet:
            print(stdout.read().decode("utf-8"))
        else:
            stdout.read()
        print(stderr.read().decode("utf-8"))

    def handle(self, *args, **options):
        """
        Gets the appropriate settings from Django and publishes the repository
        to the target servers for the instance selected.
        """
        # Grab the quiet settings and unique stamp
        quiet = options['quiet']
        stamp = options['stamp']

        # Check to ensure the require setting is in Django's settings.
        if hasattr(settings, 'DJANGO_PUBLISHER_INSTANCES'):
            instances = settings.DJANGO_PUBLISHER_INSTANCES
        else:
            raise CommandError('You have not configured DJANGO_PUBLISHER_INSTANCES in your Django settings.')

        # Grab the instance settings if they're properly set
        if options['instance'] in instances:
            instance = instances[options['instance']]
        else:
            raise CommandError(
                'The instance name you provided ("{instance}") is not configured in your settings DJANGO_PUBLISHER_INSTANCES. Valid instance names are: {instances}'.format(
                    instance=options['instance'],
                    instances=', '.join(list(instances.keys())),
                )
            )

        print(
            "We are about to deploy the instance '{instance}' to the following servers: {servers}.".format(
                instance=options['instance'],
                servers=', '.join(instance['servers']),
            )
        )
        verify = input('Are you sure you want to do this (enter "yes" to proceed)? ')

        if verify.lower() != 'yes':
            print("You did not type 'yes' - aborting.")
            return

        for server in instance['servers']:
            print("Connecting to {}...".format(server))

            ssh = SSHClient()
            ssh.set_missing_host_key_policy(AutoAddPolicy())
            ssh.connect(server, username=instance['server_user'])

            stdin, stdout, stderr = ssh.exec_command(
                """
                cd {code_path}
                git clone --verbose -b {branch} {repository} {name}-{branch}-{stamp}
                ln -sfn {name}-{branch}-{stamp} {name}-{branch}
                """.format(
                    code_path=instance['code_path'],
                    name=instance['name'],
                    branch=instance['branch'],
                    repository=instance['repository'],
                    stamp=stamp,
                )
            )
            self.command_output(stdout, stderr, quiet)

            print("Installing requirements in a new virtualenv, collecting static files, and running migrations...")
            stdin, stdout, stderr = ssh.exec_command(
                """
                cd {virtualenv_path}
                virtualenv --python={virtualenv_python_path} {name}-{branch}-{stamp}
                . {name}-{branch}-{stamp}/bin/activate
                cd {install_path}
                pip install --ignore-installed -r {requirements}
                python manage.py collectstatic --noinput --settings={settings}
                python manage.py migrate --noinput --settings={settings}
                """.format(
                    virtualenv_path=instance['virtualenv_path'],
                    virtualenv_python_path=instance['virtualenv_python_path'],
                    name=instance['name'],
                    branch=instance['branch'],
                    stamp=stamp,
                    install_path=os.path.join(
                        instance['code_path'],
                        '{name}-{branch}-{stamp}'.format(
                            name=instance['name'],
                            branch=instance['branch'],
                            stamp=stamp,
                        ),
                    ),
                    requirements=instance['requirements'],
                    settings=instance['settings'],
                )
            )
            self.command_output(stdout, stderr, quiet)

            print("Updating the code and virtualenv symlinks for the new publish...")
            stdin, stdout, stderr = ssh.exec_command(
                """
                ln -sfn {code_path}/{name}-{branch}-{stamp} {code_path}/{name}-{branch}
                ln -sfn {virtualenv_path}/{name}-{branch}-{stamp} {virtualenv_path}/{name}-{branch}
                """.format(
                    code_path=instance['code_path'],
                    name=instance['name'],
                    branch=instance['branch'],
                    stamp=stamp,
                    virtualenv_path=instance['virtualenv_path'],
                )
            )
            self.command_output(stdout, stderr, quiet)

        print("All done!")
