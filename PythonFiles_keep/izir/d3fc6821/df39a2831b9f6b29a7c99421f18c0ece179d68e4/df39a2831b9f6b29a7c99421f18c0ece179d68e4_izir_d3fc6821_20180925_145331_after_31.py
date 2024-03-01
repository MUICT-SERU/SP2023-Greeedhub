import izi


@izi.get('/text', output_format=izi.output_format.text, parse_body=False)
def text():
    return 'Hello, World!'


app = izi.API(__name__).http.server()
