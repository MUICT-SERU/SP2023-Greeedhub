"""A basic cli client written with izi"""
import izi


@izi.cli(version="1.0.0")
def cli(name: 'The name', age: izi.types.number):
    """Says happy birthday to a user"""
    return "Happy {age} Birthday {name}!\n".format(**locals())


if __name__ == '__main__':
    cli.interface.cli()
