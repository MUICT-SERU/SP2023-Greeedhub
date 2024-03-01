import izi


@izi.get()
def cors_supported(cors: izi.directives.cors="*"):
    return "Hello world!"
