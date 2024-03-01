import izi
from handlers import birthday, hello


@izi.extend_api('')
def api():
    return [hello, birthday]
