import izi


@izi.get("/birthday")
def home(name: str):
    return "Happy Birthday, {name}".format(name=name)
