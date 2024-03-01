import izi
from falcon import HTTP_400

@izi.get()
def only_positive(positive: int, response):
    if positive < 0:
        response.status = HTTP_400
