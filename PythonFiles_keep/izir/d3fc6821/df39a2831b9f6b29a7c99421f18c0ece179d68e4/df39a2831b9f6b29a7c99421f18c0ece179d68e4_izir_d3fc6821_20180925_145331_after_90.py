import izi


@izi.get()
def quick():
    return 'Serving!'


if __name__ == '__main__':
    izi.API(__name__).http.serve()
