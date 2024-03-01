import izi

API = izi.API('git')


@izi.object(name='git', version='1.0.0', api=API)
class GIT(object):
    """An example of command like calls via an Object"""

    @izi.object.cli
    def push(self, branch='master'):
        return 'Pushing {}'.format(branch)

    @izi.object.cli
    def pull(self, branch='master'):
        return 'Pulling {}'.format(branch)


if __name__ == '__main__':
    API.cli()
