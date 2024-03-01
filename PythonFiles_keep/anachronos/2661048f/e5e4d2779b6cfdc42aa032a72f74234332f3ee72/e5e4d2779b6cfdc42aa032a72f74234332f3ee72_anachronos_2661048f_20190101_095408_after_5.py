import anachronos
from anachronos.communication.anachronos_client import AnachronosClient


def setup_anachronos_client(queue):
    anachronos.set_instance(AnachronosClient(queue))


def run_wsgi(wsgi_app, port=4000):
    from werkzeug.serving import run_simple

    current_instance = anachronos.get_instance()

    def lazy_queue_initializer_wsgi_app(env, start_response):
        import anachronos
        if anachronos.get_instance() is None:
            anachronos.set_instance(current_instance)

        return wsgi_app(env, start_response)

    run_simple('localhost', port, lazy_queue_initializer_wsgi_app, processes=1, threaded=False)
