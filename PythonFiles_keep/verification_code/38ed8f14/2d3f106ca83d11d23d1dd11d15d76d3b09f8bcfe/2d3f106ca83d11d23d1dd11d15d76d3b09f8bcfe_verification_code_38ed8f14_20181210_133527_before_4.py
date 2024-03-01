import sys
import hashlib
import os.path as path
from PIL import Image, ImageFont, ImageDraw, ImageColor, ImageFilter
from random import choice, randint

def md5(s:str):
    h = hashlib.md5()
    h.update(s.encode(encoding='utf-8'))
    return h.hexdigest()

DEFAULT_FILENAME = 'default.png'

class Generator(object):
    '''
    Generator to generate Image of code and can be save into file or files
    also support hash filename.
    '''

    def __init__(self, is_hash_filename:bool=False,width:int=200,
         height:int=80, fontsize=60, fonttype=None):
        self.is_hash_filename = is_hash_filename
        self.code = ""
        self.width = width
        self.height = height
        self._fontsize = fontsize
        self._img = None

        fonttype = "fonts/Courier.dfont"
        if not fonttype and sys.platform != "darwin":
            fonttype = 'fonts/Courier.dfont'

        self.font = ImageFont.truetype(fonttype, fontsize)

    def _format_savepath(self, path_or_filename:str):
        '''
        args: path_or_filename if is dir and is_hash_filename is True, 
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
        '''
        args: save_to_path: string, need_format: bool
        return save_to_path that be formatted or not.
        '''
        if need_format:
            save_to_path = self._format_savepath(save_to_path)
        # print("debug save to path:", save_to_path)
        self._img.save(save_to_path)
        return save_to_path

    @classmethod
    def img_blur(cls, img: Image):
        width, height = img.size
        draw = ImageDraw.Draw(img)
        # 划线
        for i in range(5):
            x1=randint(0,width)
            x2=randint(0,width)
            y1=randint(0,height)
            y2=randint(0,height)
            draw.line((x1,y1,x2,y2),fill=get_rand_color())

        # 画点
        for i in range(30):
            draw.point([randint(0, width), randint(0, height)], fill=get_rand_color())
            x = randint(0, width)
            y = randint(0, height)
            draw.arc((x, y, x + 4, y + 4), 0, 90, fill=get_rand_color())

    def generate(self, code: str=""):
        '''
        create a new Image and merge with code _img
        code has a max length
        '''
        if not code:
            raise Exception("could not generate empty code: %s" % (code))
        self.code = code

        if len(code) > 6:
            raise CodeOverLenError(len(code), 6)

        self._img = Image.new('RGBA', (self.width, self.height), color=CustomColor.WHITE)
        # self._img = Image.new('RGBA', (self.width, self.height))
        basestep = int(self.width / len(code))

        for pos, c in enumerate(code):
            txt_img = self._gen_txt_img(c, self._fontsize, self.font)
            roffset = randint(-10 ,10)
            
            # set the position and paste the code image
            x, y = pos*basestep+roffset, int((self.height - txt_img.height)/2)
            
            if x < 0: 
                x = 0
            if x > self.width:
                x = self.width
            self._img.paste(txt_img, box=(x, y), mask=txt_img)

        # ImageFilter.GaussianBlur
        self._img = self._img.filter(ImageFilter.GaussianBlur(radius=2))
        # blur image
        self.img_blur(self._img)

    @classmethod
    def _gen_txt_img(cls, text: str, fontsize: int, font):
        img = Image.new('RGBA', (fontsize, fontsize))
        text_draw = ImageDraw.Draw(img)
        rcolor = CustomColor.rand_color() # ran font color
        text_draw.text((0,0), text, fill=rcolor, font=font)
        img = img.rotate(angle=randint(-30,90), expand=False)
        return img

    def generate_multi(self, codes: list, folder: str):
        # check folder existed
        if not path.exists(folder):
            raise Exception("could not open folder: %s" % folder)
        
        _hash_dict = dict()

        for code in codes:
            self.generate(code)
            save_to_path = "{code}.png".format(code=code)
            if self.is_hash_filename:
                save_to_path = md5(code)
            # if duplicate name
            if save_to_path in _hash_dict:
                _hash_dict[save_to_path] = _hash_dict[save_to_path]+1
                save_to_path = "{ori}_{cnt}.png".format(ori=save_to_path, cnt=_hash_dict[save_to_path])
            else:
                _hash_dict.update({save_to_path: 1})
            
            save_to_path = path.join(folder, save_to_path)
            # now save to file
            self.save(save_to_path, need_format=False)


def get_rand_color():
    return CustomColor.rand_color()

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


class CodeOverLenError(Exception):

    def __init__(self, len, limit_len):
        self.len = len
        self.limit_len = limit_len

    def __str__(self):
        return "code length(%d) is out range of (%d)" % (self.len, self.limit_len)