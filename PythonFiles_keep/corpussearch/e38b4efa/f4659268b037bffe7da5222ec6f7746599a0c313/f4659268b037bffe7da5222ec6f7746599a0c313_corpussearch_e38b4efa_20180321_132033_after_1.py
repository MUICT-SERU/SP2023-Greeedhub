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

class CorpusML(CorpusTextSearch):
    """
    Machine learning routines for corpussearch.

    Trains gensim's Word2Vec for data contained in 'colname' column. Usefull
    to obtain word-contexts for additional searches. Expects additional
    inital key: language, to determine tokenizers, lemmatizers, and stopwords.
    Model parameters are given as a tuple of numbers,e.g.,
    '(workers=4,min_count=5,features=300)'.

    Currently supported languages (using CLTK and NLTK): latin, greek, english

    Example:
            >>> ml1 = CorpusML(
                            pathDF='/path/to/dataframe/file.xlsx',
                            dataType='excel',
                            dataIndex='single',
                            colname='main',
                            language='english'
                            )

            >>> ml1.trainModel()

            >>> ml1.getSimilarContext('word1')
            True
    """
    def __init__(
            self, pathDF, language='english',
            dataType='pickle', dataIndex='multi', colname='text',
            maxValues=2500, pathMeta=False, pathType=False, showLogging=False,
            model_params=(4,5,300)
            ):

        super(CorpusML, self).__init__(
            pathDF, dataType, dataIndex, colname,
            maxValues, pathMeta, pathType
            )

        if showLogging:
            logging.basicConfig(
                format='%(asctime)s : %(levelname)s : %(message)s',
                level=logging.INFO
                )

        self.model = gensim.models.Word2Vec(
            workers=model_params[0],
            min_count=model_params[1],
            size=model_params[2]
            )

        # self.model.random.seed(42)

        self.language = language

        if self.language == 'latin' or self.language == 'greek':
            from cltk.corpus.utils.importer import CorpusImporter
            corpus_importer = CorpusImporter(self.language)
            corpus_importer.import_corpus(
                '{0}_models_cltk'.format(self.language)
                )
            from cltk.stem.lemma import LemmaReplacer
            from cltk.tokenize.word import nltk_tokenize_words as tokenizer
            lemmatizer = LemmaReplacer(self.language)
            if self.language == 'latin':
                from cltk.stem.latin.j_v import JVReplacer
                from cltk.stop.latin.stops import STOPS_LIST as stopwords
                self.jvreplacer = JVReplacer()
            elif self.language == 'greek':
                from cltk.stop.greek.stops import STOPS_LIST as stopwords
        elif self.language == 'english' or 'german':
            import nltk
            nltk.download('stopwords')
            from nltk.stem import WordNetLemmatizer
            from nltk.tokenize import word_tokenize as tokenizer
            from nltk.corpus import stopwords
            stopwords = stopwords.words(self.language)
            lemmatizer = WordNetLemmatizer()
        else:
            raise ValueError(
                'Could not find lemmatizer, tokenizer,\
                 and stopwords for chosen language.')
        self.lemmatizer = lemmatizer
        self.tokenizer = tokenizer
        self.stopwords = stopwords

    def convert(self, row):
        """
        Helper function: Converts input data from 'colname'-column to a
        tokenized, lemmatized, and cleaned word list without stopwords.

        Additionaly, for latin language CLTK's jvreplace is applied.
        """
        reg = re.compile('[^a-zA-Z0-9]')
        if type(row) == str:
            sentence = self.tokenizer(row)
            sentence = [x.lower() for x in sentence]
            sentence = [x for x in sentence if x not in self.stopwords]
            sentence = [reg.sub('', x) for x in sentence]
            sentence = [x for x in sentence if x and len(x) > 1]
            sentence = [x.strip('0123456789') for x in sentence]
            if self.language == 'latin':
                sentence = [self.jvreplacer.replace(word) for word in sentence]
            try:
                sentence = self.lemmatizer.lemmatize(sentence)
            except:
                pass
            return sentence

    def saveTrainData(self):
        """
        Creates new training data column,
        by applying convert() to 'colname' column.
        """
        self.dataframe['training_data'] = self.dataframe[self.column].apply(
            lambda row: self.convert(row)
        )
        self.tempFile = tempfile.NamedTemporaryFile(delete=False)
        self.dataframe.to_pickle(self.tempFile.name)
        return

    def buildVocab(self):
        """
        Builds model vocabulary.
        """
        try:
            self.tempFile
        except AttributeError:
            self.saveTrainData()
        loadedData = pd.read_pickle(self.tempFile)
        self.training_data = loadedData.training_data.values.tolist()
        self.model.build_vocab(self.training_data)
        return

    def trainModel(self):
        """
        Trains model based on created training data.
        """
        try:
            self.training_data
        except AttributeError:
            self.buildVocab()
        self.model.train(
            self.training_data,
            total_examples=self.model.corpus_count,
            epochs=self.model.epochs
            )
        return

    def getSimilarContext(self, word):
        """
        Returns words occuring in the corpus with similar context. If the word
        is not contained in the training vocabulary, a similiar word is choosen
        using difflib's get_close_matches.
        """
        vocabulary = self.model.wv.vocab.keys()
        if word in vocabulary:
            res = self.model.wv.most_similar(word)
            return res
        else:
            simWord = difflib.get_close_matches(word, vocabulary, 1)
            print('Using similar word: {0}'.format(simWord[0]))
            res = self.model.wv.most_similar(simWord)
            return res
