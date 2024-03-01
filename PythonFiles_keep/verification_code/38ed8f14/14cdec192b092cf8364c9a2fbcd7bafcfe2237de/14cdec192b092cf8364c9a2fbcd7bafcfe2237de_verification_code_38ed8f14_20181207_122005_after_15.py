import hashlib
import os.path as path
from PIL import Image, ImageFont, ImageDraw, ImageColor
from random import choice

def md5(s:str):
    h = hashlib.md5()
    h.update(s.encode(encoding='utf-8'))
    return h.hexdigest()

DEFAULT_FILENAME = 'default.png'

class Generator(object):
    '''Generator to generate Image of code and can be save into file or files
    also support hash filename.
    '''

    def __init__(self, is_hash_filename:bool=False, code:str="", 
        width:int=100, height:int=40, fontsize=20):
        self.is_hash_filename = is_hash_filename
        self.code = code
        self.img = None
        self.width = width
        self.height = height
        self._fontsize = fontsize
        # TODO: related to system
        self.font = ImageFont.truetype('fonts/STHeiti Light.ttc', fontsize) 

    def _format_savepath(self, path_or_filename:str):
        '''args: path_or_filename if is dir and is_hash_filename is True, 
        then new a hash filename
        return: formated path_or_filename
        '''

        if path.isdir(path_or_filename):
            if self.is_hash_filename:
                name = "{hash}.png".format(hash=md5(self.code))
            else:
                name = "{code}.png".format(code=self.code if self.code else "default")
            path_or_filename= path.join(path_or_filename, name)
            return path_or_filename
        
        # not dir as a filename
        if not path.exists(path_or_filename):
            print("verifycode error: could not found path: {path}".format(path=path_or_filename))
            return DEFAULT_FILENAME
        
        return path_or_filename

    def save(self, save_to_path:str, need_format=True):
        if need_format:
            save_to_path = self._format_savepath(save_to_path)
        print("debug save to path:", save_to_path)
        self.img.save(save_to_path)

    def generate(self, code: str):
        '''create a new Image and merge with code img
        code has a max length
        '''
        if not code:
            raise Exception("could not generate empty code: %s" % (code))
        
        if len(code) > 6:
            print("max limit is 6 size of code")
            return

        self.img = Image.new('RGBA', (self.width, self.height), color=CustomColor.WHITE)
        draw = ImageDraw.Draw(self.img)
        basestep = self.width / len(code)
        
        fonty = (self.height - self._fontsize) /2

        for pos, c in enumerate(code):
            rcolor = CustomColor.rand_color() # ran font color
            roffset = -10 # [+fontsize - -fontsize]
            if pos == 0 and roffset < 0:
                roffset = 0
            draw.text((pos*basestep+roffset, fonty), c, fill=rcolor, font=self.font)
        
        
    def generate_multi(self, codes: list, folder: str):
        # check folder existed
        if not path.exists(folder):
            raise Exception("could not open folder: %s" % folder)
        
        _hash_dict = dict()

        for code in codes:
            self.generate(code)
            # initial save_to_path name
            save_to_path = "{code}.png".format(code)
            # if need hash_name
            if self.is_hash_filename:
                save_to_path = md5(code)
            # if duplicate name
            if save_to_path in _hash_dict:
                save_to_path = "{ori}_1".format(save_to_path)
            # now save to file
            self.save(save_to_path, need_format=False)


class CustomColor(object):

    WHITE = ImageColor.getcolor('#ffffff', 'RGBA')
    BLACK = ImageColor.getcolor('#000000', 'RGBA')
    GRAY = ImageColor.getcolor('#3e3e3e', 'RGBA')
    RED = ImageColor.getcolor('#ff1107', 'RGBA')
    GREEN = ImageColor.getcolor('#1bff46', 'RGBA')
    YELLOW = ImageColor.getcolor('#ffbf13', 'RGBA')
    BLUE = ImageColor.getcolor('#235aff', 'RGBA')

    _colors = [
        BLACK,
        GRAY,
        RED,
        GREEN,
        YELLOW,
        BLUE,
    ]

    @classmethod
    def rand_color(cls):
        ''' return an random color in class._colors 
        [BLACK,GRAY,RED,GREEN,YELLOW,BLUE]
        '''
        return choice(cls._colors)