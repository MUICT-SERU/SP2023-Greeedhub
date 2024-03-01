import izi

api = izi.API(__name__)
api.http.add_middleware(izi.middleware.CORSMiddleware(api, max_age=10))


@izi.get('/demo')
def get_demo():
    return {'result': 'Hello World'}
