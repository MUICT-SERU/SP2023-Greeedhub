import izi


@izi.get("/hello")
def hello(name: str="World"):
    return "Hello, {name}".format(name=name)
