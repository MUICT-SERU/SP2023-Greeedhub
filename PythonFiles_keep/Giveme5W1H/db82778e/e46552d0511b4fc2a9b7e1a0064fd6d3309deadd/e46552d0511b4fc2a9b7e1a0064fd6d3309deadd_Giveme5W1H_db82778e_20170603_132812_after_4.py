import logging
import os
import sys
# Add path to allow execution though console
sys.path.insert(0, '/'.join(os.path.realpath(__file__).split('/')[:-2]))
#from timeit import default_timer as timer
import extractor.extractor
from extractor.preprocessors.preprocessor_core_nlp import Preprocessor
from extractor.extractor import FiveWExtractor

from extractor.tools.news_please.processor.simple_logger import SimpleLogger
from extractor.tools.news_please.handler import Handler
from extractor.tools.news_please.processor.learn_weights import LearnWeights

"""
This is a simple example on how to use the extractor in combination with NewsPlease files
"""

core_nlp_host = 'http://localhost:9000'

if __name__ == '__main__':
    log = logging.getLogger('GiveMe5W')
    log.setLevel(logging.DEBUG)
    sh = logging.StreamHandler()
    sh.setLevel(logging.DEBUG)
    log.addHandler(sh)
    
    #extractor = FiveWExtractor(Preprocessor(core_nlp_host))
    inputPath = os.path.dirname(__file__) + '/input'
    outputPath = os.path.dirname(__file__) + '/output'
    Handler(inputPath).setOutputPath(outputPath).addProcessor( SimpleLogger() ).process()