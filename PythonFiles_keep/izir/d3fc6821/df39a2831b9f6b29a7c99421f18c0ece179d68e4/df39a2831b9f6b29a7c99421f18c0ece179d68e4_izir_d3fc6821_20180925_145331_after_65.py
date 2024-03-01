# pylint: disable=C0111, E0401
""" API Entry Point """

import izi


@izi.get("/", output=izi.output_format.html)
def base():
    return "<h1>hello world</h1>"


@izi.get("/add", examples="num=1")
def add(num: izi.types.number = 1):
    return {"res" : num + 1}
