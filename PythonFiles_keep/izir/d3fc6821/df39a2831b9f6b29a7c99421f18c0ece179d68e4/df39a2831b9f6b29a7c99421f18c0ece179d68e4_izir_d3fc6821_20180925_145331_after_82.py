import izi
import part_1
import part_2


@izi.get('/')
def say_hi():
    return "Hi from root"


@izi.extend_api()
def with_other_apis():
    return [part_1, part_2]
