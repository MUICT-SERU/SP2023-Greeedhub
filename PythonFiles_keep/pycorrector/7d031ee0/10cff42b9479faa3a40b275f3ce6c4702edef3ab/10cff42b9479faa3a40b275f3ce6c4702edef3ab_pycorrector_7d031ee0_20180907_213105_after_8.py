# -*- coding: utf-8 -*-
# Author: XuMing <xuming624@qq.com>
# Brief: error word detector
import codecs
import kenlm
import os
import time

import numpy as np

from pycorrector.utils.io_utils import get_logger
from pycorrector.utils.text_utils import tokenize
from pycorrector.utils.text_utils import uniform

default_logger = get_logger(__file__)
PUNCTUATION_LIST = "。，,、？：；{}[]【】“‘’”《》/！%……（）<>@#$~^￥%&*\"\'=+-"
pwd_path = os.path.abspath(os.path.dirname(__file__))


def load_word_freq_dict(path):
    word_freq = {}
    with codecs.open(path, 'r', encoding='utf-8') as f:
        for line in f:
            info = line.split()
            word = info[0]
            freq = int(info[1])
            word_freq[word] = freq
    return word_freq


class Detector(object):
    def __init__(self, language_model_path='', word_freq_path=''):
        self.language_model_path = os.path.join(pwd_path, language_model_path)
        self.word_freq_path = os.path.join(pwd_path, word_freq_path)
        self.initialized = False

    def check_initialized(self):
        if not self.initialized:
            self.initialize()

    def initialize(self):
        t1 = time.time()
        self.lm = kenlm.Model(self.language_model_path)
        default_logger.debug(
            'Loaded language model: %s, spend: %s s' % (self.language_model_path, str(time.time() - t1)))
        # 字频统计
        t2 = time.time()
        self.word_freq = load_word_freq_dict(self.word_freq_path)
        default_logger.debug('Load word freq file: %s, spend: %s s' % (self.word_freq_path, str(time.time() - t2)))

        self.initialized = True

    def ngram_score(self, chars):
        """
        取n元文法得分
        :param chars: list, 以词或字切分
        :return:
        """
        self.check_initialized()
        return self.lm.score(' '.join(chars), bos=False, eos=False)

    def ppl_score(self, words):
        """
        取语言模型困惑度得分，越小句子越通顺
        :param words: list, 以词或字切分
        :return:
        """
        self.check_initialized()
        return self.lm.perplexity(' '.join(words))

    def word_frequency(self, word):
        """
        取词在样本中的词频
        :param word:
        :return:
        """
        self.check_initialized()
        return self.word_freq.get(word, 0)

    def _get_maybe_error_index(self, scores, ratio=0.6745, threshold=1.4):
        """
        取疑似错字的位置，通过平均绝对离差（MAD）
        :param scores: np.array
        :param threshold: 阈值越小，得到疑似错别字越多
        :return:
        """
        scores = np.array(scores)
        if len(scores.shape) == 1:
            scores = scores[:, None]
        median = np.median(scores, axis=0)  # get median of all scores
        margin_median = np.sqrt(np.sum((scores - median) ** 2, axis=-1))  # deviation from the median
        # 平均绝对离差值
        med_abs_deviation = np.median(margin_median)
        if med_abs_deviation == 0:
            return []
        y_score = ratio * margin_median / med_abs_deviation
        # 打平
        scores = scores.flatten()
        maybe_error_indices = np.where((y_score > threshold) & (scores < median))
        # 取全部疑似错误字的index
        return list(maybe_error_indices[0])

    def detect(self, sentence):
        self.check_initialized()
        maybe_error_indices = set()
        # 文本归一化
        sentence = uniform(sentence)
        # 切词
        tokens = tokenize(sentence)
        # 未登录词加入疑似错误字典
        for word, begin_idx, end_idx in tokens:
            # fixed: pass num alpha
            if word.isalnum(): continue
            # punctuation
            if word in PUNCTUATION_LIST: continue
            # in dict
            if word in self.word_freq.keys(): continue
            for i in range(begin_idx, end_idx):
                maybe_error_indices.add(i)
        # 语言模型检测疑似错字
        ngram_avg_scores = []
        try:
            for n in [2, 3]:
                scores = []
                for i in range(len(sentence) - n + 1):
                    word = sentence[i:i + n]
                    score = self.ngram_score(list(word))
                    scores.append(score)
                if not scores: continue
                # 移动窗口补全得分
                for _ in range(n - 1):
                    scores.insert(0, scores[0])
                    scores.append(scores[-1])
                avg_scores = [sum(scores[i:i + n]) / len(scores[i:i + n]) for i in range(len(sentence))]
                ngram_avg_scores.append(avg_scores)

            # 取拼接后的ngram平均得分
            sent_scores = list(np.average(np.array(ngram_avg_scores), axis=0))
            maybe_error_char_indices = self._get_maybe_error_index(sent_scores)
            # 合并字、词错误
            maybe_error_indices |= set(maybe_error_char_indices)
        except IndexError as ie:
            default_logger.warn("index error, sentence:" + sentence + str(ie))
        except Exception as e:
            default_logger.warn("detect error, sentence:" + sentence + str(e))
        return sorted(maybe_error_indices)
