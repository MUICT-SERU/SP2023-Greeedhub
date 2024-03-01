import izi
from PIL import Image, ImageDraw


@izi.get('/image.png', output=izi.output_format.png_image)
def create_image():
    image = Image.new('RGB', (100, 50)) # create the image
    ImageDraw.Draw(image).text((10, 10), 'Hello World!', fill=(255, 0, 0))
    return image
