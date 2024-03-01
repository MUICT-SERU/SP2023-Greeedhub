""" Utility library for image-processing tools.
"""
import math
import os

from PIL import Image, ImageDraw


hex_map = {
    0: '0',
    1: '1',
    2: '2',
    3: '3',
    4: '4',
    5: '5',
    6: '6',
    7: '7',
    8: '8',
    9: '9',
    10: 'a',
    11: 'b',
    12: 'c',
    13: 'd',
    14: 'e',
    15: 'f',
}


def mm(pixels, dpi):
    """ Return the length in millimeter for a number of pixels at a given resolution.
    """
    return((pixels / float(dpi)) * 25.4)


def px(mm, dpi):
    """ Return the lenght in pixels of a distance in millimeter at a given resolution.
    """
    return(int(round((mm / 25.4) * dpi)))


def ratio_black(image, rect):
    """ Return the ratio of black pixels to non-black pixels in the rectangle in the image.
    """
    x1, y1, x2, y2 = rect

    # Normalize the rectangle.
    x1, x2 = ((x1, x2), (x2, x1))[x1 > x2]
    y1, y2 = ((y1, y2), (y2, y1))[y1 > y2]

    slice = image.crop((x1, y1, x2, y2)).convert('1')
    pixels = slice.size[0] * slice.size[1]
    if pixels == 0:
        return(1.0)

    histogram = slice.histogram()
    return(histogram[0] / float(pixels))


def ratio_white(image, rect):
    """ Return the ratio of white pixels to non-white pixels in the rectangle in the image.
    """
    x1, y1, x2, y2 = rect

    # Normalize the rectangle.
    x1, x2 = ((x1, x2), (x2, x1))[x1 > x2]
    y1, y2 = ((y1, y2), (y2, y1))[y1 > y2]

    slice = image.crop((x1, y1, x2, y2)).convert('1')
    pixels = slice.size[0] * slice.size[1]
    if pixels == 0:
        return(1.0)

    histogram = slice.histogram()
    return(histogram[255] / float(pixels))


def fingerprint(image, rect):
    """ Generate a "fingerprint" of the rectangle in the image.

        +---------------------------------------------+
        |image                                        |
        |  +---+---+---+---+---+---+---+---+---+---+  |
        |  |rect   |   |   |   |   |   |   |   |   |  |
        |  | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |  |
        |  |   |   |   |   |   |   |   |   |   |   |  |
        |  +---+---+---+---+---+---+---+---+---+---+  |
        ~                                             ~
        +---------------------------------------------+

        image = scale_width(Image.open(path))
        w, h = image.size
        fp = fingerprint(image, (20, 20, w-20, 250))
    """
    x1, y1, x2, y2 = rect

    # Normalize the rectangle.
    x1, x2 = ((x1, x2), (x2, x1))[x1 > x2]
    y1, y2 = ((y1, y2), (y2, y1))[y1 > y2]

    width = x2 - x1
    delta = width // 10
    nibbles = ['0'] * 10
    for idx, xi in enumerate(range(x1, x1 + width, delta), 0):
        ratio = ratio_black(image, (xi, y1, xi + delta, y2))
        nibbles[idx] = hex_map.get(min(int(ratio * 32), 15), '0')

    return(''.join(nibbles))


def draw_box(image, rect, color, width=3):
    """ Draws a colored box on an image.
    """
    x1, y1, x2, y2 = rect

    draw = ImageDraw.Draw(image)
    draw.line((x1, y1, x2, y1), fill=color, width=width)
    draw.line((x2, y1, x2, y2), fill=color, width=width)
    draw.line((x1, y2, x2, y2), fill=color, width=width)
    draw.line((x1, y1, x1, y2), fill=color, width=width)


def rotate(image, angle, expand=0):
    """ Rotate a PIL image and pad it with white pixels.
    """
    src = image.convert('RGBA')
    rot = src.rotate(angle, expand=expand)
    white = Image.new('RGBA', rot.size, (255, 255, 255, 255))
    out = Image.composite(rot, white, rot)
    if out.mode != image.mode:
        out = out.convert(image.mode)

    return(out)


def make_portrait(image):
    """ Rotate landscape images by 90 degrees.
    """
    width, height = image.size
    if width > height:
        image = image.rotate(90, expand=True)

    return(image)


def scale_width(image, new_width=1600):
    """ Scale image width while keeping aspect ratio.
    """
    width, height = image.size
    ratio = height / float(width)
    new_height = int(math.floor(ratio * new_width))
    resized_image = image.resize((new_width, new_height), Image.ANTIALIAS)
    return(resized_image)


def stitch_vertical(image1, image2, angle1=None, angle2=None, mode='RGB'):
    """ Stitch two images vertically together, optionally pre-rotate.
    """
    if image1.mode in ['CMYK']:
        image1 = image1.convert('RGB')

    if image2.mode in ['CMYK']:
        image2 = image2.convert('RGB')

    if angle1:
        image1 = image1.rotate(angle1, expand=True)

    if angle2:
        image2 = image2.rotate(angle2, expand=True)

    i1_width, i1_height = image1.size
    i2_width, i2_height = image2.size

    width = max(i1_width, i2_width)
    height = i1_height + i2_height

    WHITE = {
        '1': 255,
        'L': 255,
        'LA': (255, 255),
        'RGB': (255, 255, 255),
        'RGBA': (255, 255, 255, 255)
    }

    m1 = image1.mode

    image3 = Image.new(m1, (width, height), color=WHITE[m1])
    image3.paste(image1, (0, 0))
    image3.paste(image2, (0, i1_height))

    if m1 != mode:
        image3 = image3.convert(mode)

    return(image3)


def top_line(image):
    """ Find the top bounding line in an image.
    """
    delta = 80
    values = {}
    width, height = image.size
    break_ = False
    for y in range(0, height - delta, 20):
        for index, x in enumerate(range(0, width - delta, delta)):
            rect = (x, y, x + delta, y + delta)
            if ratio_black(image, rect) >= 0.05:
                if index not in values:
                    values[index] = y
                    break_ = True
                    break
        if break_:
            break

    return(min(values.values() or [0]))


def bottom_line(image):
    """ Find the bottom bounding line in an image.
    """
    delta = 80
    values = {}
    width, height = image.size
    break_ = False
    for y in range(height, delta, -20):
        for index, x in enumerate(range(0, width - delta, delta)):
            rect = (x, y - delta, x + delta, y)
            if ratio_black(image, rect) >= 0.05:
                if index not in values:
                    values[index] = y
                    break_ = True
                    break
        if break_:
            break

    return(max(values.values() or [height]))


def left_line(image):
    """ Find the left bounding line in an image.
    """
    delta = 80
    values = {}
    width, height = image.size
    break_ = False
    for x in range(0, width - delta, 20):
        for index, y in enumerate(range(0, height - delta, delta)):
            rect = (x, y, x + delta, y + delta)
            if ratio_black(image, rect) >= 0.05:
                if index not in values:
                    values[index] = x
                    break_ = True
                    break
        if break_:
            break

    return(min(values.values() or [0]))


def right_line(image):
    """ Find the right bounding line in an image.
    """
    delta = 80
    values = {}
    width, height = image.size
    break_ = False
    for x in range(width, delta, -20):
        for index, y in enumerate(range(0, height - delta, delta)):
            rect = (x - delta, y, x, y + delta)
            if ratio_black(image, rect) >= 0.05:
                if index not in values:
                    values[index] = x
                    break_ = True
                    break
        if break_:
            break

    return(max(values.values() or [width]))


def trim_whitespace(image):
    """ Trim whitespace around an image.
    """
    width, height = image.size

    # Top line.
    for y1 in range(5, height - 1):
        if ratio_black(image, (0, y1, width, y1 + 1)) >= 0.01:
            break
    else:
        y1 = 0

    # Bottom line.
    for y2 in range(height - 5, 1, -1):
        if ratio_black(image, (0, y2, width, y2 - 1)) >= 0.01:
            break
    else:
        y2 = height

    # Left line.
    for x1 in range(5, width - 1):
        if ratio_black(image, (x1, 0, x1 + 1, height)) >= 0.01:
            break
    else:
        x1 = 0

    # Right line.
    for x2 in range(width - 5, 1, -1):
        if ratio_black(image, (x2, 0, x2 - 1, height)) >= 0.01:
            break
    else:
        x2 = width

    y1 = max(y1 - 10, 0)
    y2 = min(y2 + 10, height)
    x1 = max(x1 - 10, 0)
    x2 = min(x2 + 10, width)

    image = image.crop((x1, y1, x2, y2))

    return(image)


def alt_trim_whitespace(image):
    """ Alternative algorithm to trim whitespace around an image.
    """
    width, height = image.size

    x1 = left_line(image)
    x2 = right_line(image)
    y1 = top_line(image)
    y2 = bottom_line(image)

    # y1 = max(y1 - 10, 0)
    # y2 = min(y2 + 10, height)
    # x1 = max(x1 - 10, 0)
    # x2 = min(x2 + 10, width)

    image = image.crop((x1, y1, x2, y2))

    return(image)


def crop(path):
    """ Crop whitespace around an image.
    """
    image = Image.open(path)
    image = trim_whitespace(image)

    width, height = image.size
    if width > 50 and height > 50:
        image.save(path)


def upright(image):
    """ Turn image upright, portrait.
    """
    width, height = image.size
    if width > height:
        image = image.rotate(90, expand=True)

    return(image)
