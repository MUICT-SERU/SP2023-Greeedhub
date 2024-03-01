# -*- coding: utf-8 -*-
import pandas as pd
import re
import difflib
import logging
import os
import tempfile
import gensim
import requests
from citableclass.base import Citable
from .base import CorpusTextSearch

logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s',
    level=logging.INFO
    )


class CorpusML(CorpusTextSearch):

    def __init__(
            self, pathDF, language='english',
            dataType='pickle', dataIndex='multi', colname='text',
            maxValues=2500, pathMeta=False, pathType=False
            ):

        super(CorpusML, self).__init__(
            pathDF, dataType, dataIndex, colname,
            maxValues, pathMeta, pathType
            )

        self.model = gensim.models.Word2Vec(
            workers=4, min_count=5, size=300
            )

        self.model.random.seed(42)

        self.language = language

        if self.language == 'latin':
            from cltk.stem.lemma import LemmaReplacer
            from cltk.stem.latin.j_v import JVReplacer
            from cltk.stop.latin.stops import STOPS_LIST as stopwords
            from cltk.tokenize.word import nltk_tokenize_words as tokenizer
            self.jvreplacer = JVReplacer()
            lemmatizer = LemmaReplacer('latin')

        self.lemmatizer = lemmatizer
        self.tokenizer = tokenizer
        self.stopwords = stopwords

    def convert(self, row):
        reg = re.compile('[^a-zA-Z0-9]')
        if type(row) == str:
            sentence = self.tokenizer(row)
            sentence = [x.lower() for x in sentence]
            sentence = [x for x in sentence if x not in self.stopwords]
            sentence = [x for x in sentence if x and len(x) > 1]
            sentence = [reg.sub('', x) for x in sentence]
            sentence = [x.strip('0123456789') for x in sentence]
            if self.language == 'latin':
                sentence = [self.jvreplacer.replace(word) for word in sentence]
            try:
                sentence = self.lemmatizer.lemmatize(sentence)
            except:
                pass
            return sentence

    def saveTrainData(self):
        self.dataframe['training_data'] = self.dataframe[self.column].apply(
            lambda row: self.convert(row)
        )
        self.tempFile = tempfile.NamedTemporaryFile(delete=False)
        self.dataframe.to_pickle(self.tempFile.name)
        return

    def buildVocab(self):
        loadedData = pd.read_pickle(self.tempFile)
        self.training_data = loadedData.training_data.values.tolist()
        self.model.build_vocab(training_data)
        return

    def trainModel(self):
        self.model.train(
            self.training_data,
            total_examples=self.model.corpus_count,
            epochs=self.model.epochs
            )
        return

    def getSimilarContext(word):
        vocabulary = self.model.wv.vocab.keys()
        if word in vocabulary:
            res = self.model.wv.most_similar(word)
            return res
        else:
            simWord = difflib.get_close_matches(word, vocabulary, 1)
            print('Using similar word: {0}'.format(simWord[0]))
            res = self.model.wv.most_similar(simWord)
            return res
