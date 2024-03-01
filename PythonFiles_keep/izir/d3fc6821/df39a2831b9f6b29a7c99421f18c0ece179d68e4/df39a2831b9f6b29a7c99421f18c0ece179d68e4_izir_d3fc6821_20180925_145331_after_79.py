import example_resource
import izi


@izi.get()
def hello():
    return example_resource.hi()
