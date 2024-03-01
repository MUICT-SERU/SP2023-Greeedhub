# -*- coding: utf-8 -*-
# Author: XuMing <xuming624@qq.com>
# Brief: 
from pycorrector.util import *
from pypinyin import pinyin, lazy_pinyin
import enchant

# traditional simplified
traditional_sentence = '憂郁的臺灣烏龜'
simplified_sentence = traditional2simplified(traditional_sentence)
print(simplified_sentence)

simplified_sentence = '忧郁的台湾乌龟'
traditional_sentence = simplified2traditional(simplified_sentence)
print(traditional_sentence)

print(pinyin('中心'))  # 带音调
print(pinyin('中心', heteronym=True))  # 多音字
print(lazy_pinyin('中心'))  # 不带音调


print(tokenize('小姑娘蹦蹦跳跳的去了她外公家'))

# 判断拼音还是英文
en_dict = enchant.Dict("en_US")
print(en_dict.check("hello"))
print(en_dict.check("hello boy what is your name"))
strs = "hello boy what is your name"
flag = False
for word in strs:
    if en_dict.check(word):
        flag = True
    else:
        flag = False
        break
print(flag)
print(en_dict.check("zhangsan"))
print(en_dict.check("zhangsan ni zai zhe li ma ?"))