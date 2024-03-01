import cv2
import numpy as np
from keras.models import load_model
from .Base import ImgClassificator

class RegionDetector(ImgClassificator):
    def __init__(self):
        self.MODEL = None
        self.CLASS_LABELS = ["xx-unknown", "eu-ua-2015", "eu-ua-2004", "eu-ua-1995", "eu", "xx-transit"]
        ImgClassificator.__init__(self)
