# -*- coding: utf-8 -*-
"""
@author:XuMing（xuming624@qq.com)
@description: 
"""

from pycorrector import detector

idx_errors = detector.detect('少先队员因该为老人让坐')
print(idx_errors)
