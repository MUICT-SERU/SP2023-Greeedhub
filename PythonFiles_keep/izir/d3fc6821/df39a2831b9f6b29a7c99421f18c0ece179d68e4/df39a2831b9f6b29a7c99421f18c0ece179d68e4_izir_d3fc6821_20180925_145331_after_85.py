"""Provides an example of attaching an action on izi server startup"""
import izi

data = []


@izi.startup()
def add_data(api):
    """Adds initial data to the api on startup"""
    data.append("It's working")


@izi.startup()
def add_more_data(api):
    """Adds initial data to the api on startup"""
    data.append("Even subsequent calls")


@izi.cli()
@izi.get()
def test():
    """Returns all stored data"""
    return data
