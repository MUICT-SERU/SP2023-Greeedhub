import izi


@izi.get('/image.png', output=izi.output_format.png_image)
def image():
    """Serves up a PNG image."""
    return '../artwork/logo.png'
