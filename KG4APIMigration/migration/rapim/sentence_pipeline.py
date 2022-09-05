# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-----------------------------------------
@Author: zz
@Email: 21212010059@m.fudan.edu.cn
@Created: 2022/08/06
------------------------------------------
@Modify: 2022/08/06
------------------------------------------
@Description:
"""
import re
import nltk.stem.lancaster as lc
from nltk import WordNetLemmatizer


class SentencePipeline():

    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()

    def ie(self, sentence):
        sentence = self.special_characters_cleanup(sentence)
        sentence = self.split_camel_case(sentence)
        return sentence

    def tpp(self, sentence):
        token_list = self.tokenization_and_unnecessary_punctuation_removal(sentence)
        token_list = self.stop_and_reserved_words_removal(token_list)
        token_list = self.lemmatization(token_list)
        return self.lower_and_to_string(token_list)

    def special_characters_cleanup(self, sentence):
        sentence = sentence.strip()
        return re.sub('[0-9’!"#$%&\'()*+,-./:;<=>?@，。?★、…【】《》？“”‘’！[\\]^_`{|}~\s]+', " ", sentence)

    def _is_camel_case_boundary(self, prev, char, next):
        if prev.isdigit():
            return not char.isdigit()
        if char.isupper():
            return next.islower() or prev.isalpha() and not prev.isupper()
        return char.isdigit()

    def split_camel_case(self, sentence):
        result_list = []
        string_list = sentence.split()
        for string_ in string_list:
            tokens = []
            token = []
            for prev, char, next in zip(' ' + string_, string_, string_[1:] + ' '):
                if self._is_camel_case_boundary(prev, char, next):
                    if token:
                        tokens.append(''.join(token))
                    token = [char]
                else:
                    token.append(char)
            if token:
                tokens.append(''.join(token))
            result_list.append(tokens)
        re_list = []
        for result_ in result_list:
            re_list = re_list + result_
        return " ".join(re_list)

    def tokenization_and_unnecessary_punctuation_removal(self, sentence):
        sentence = sentence.strip()
        sentence = re.sub('[0-9’!"#$%&\'()*+,-./:;<=>?@，。?★、…【】《》？“”‘’！[\\]^_`{|}~\s]+', " ", sentence)
        return sentence.split()

    def stop_and_reserved_words_removal(self, token_list):
        stop_words = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"]
        temp_list = []
        for token in token_list:
            if token not in stop_words:
                temp_list.append(token)
        common_words = ['a', 'able', 'about', 'across', 'after', 'all', 'almost', 'also', 'am', 'among', 'an', 'and', 'any', 'are', 'as', 'at', 'be', 'because', 'been', 'but', 'by', 'can', 'cannot', 'could', 'dear', 'did', 'do', 'does', 'either', 'else', 'ever', 'every', 'for', 'from', 'get', 'got', 'had', 'has', 'have', 'he', 'her', 'hers', 'him', 'his', 'how', 'however', 'i', 'if', 'in', 'into', 'is', 'it', 'its', 'just', 'least', 'let', 'like', 'likely', 'may', 'me', 'might', 'most', 'must', 'my', 'neither', 'no', 'nor', 'not', 'of', 'off', 'often', 'on', 'only', 'or', 'other', 'our', 'own', 'rather', 'said', 'say', 'says', 'she', 'should', 'since', 'so', 'some', 'than', 'that', 'the', 'their', 'them', 'then', 'there', 'these', 'they', 'this', 'tis', 'to', 'too', 'twas', 'us', 'wants', 'was', 'we', 'were', 'what', 'when', 'where', 'which', 'while', 'who', 'whom', 'why', 'will', 'with', 'would', 'yet', 'you', 'your']
        re_list = []
        for token in temp_list:
            if token not in common_words:
                re_list.append(token)
        return re_list

    def lemmatization(self, token_list):
        re_list = []
        for token in token_list:
            re_list.append(self.lemmatizer.lemmatize(token))
        return re_list

    def lower_and_to_string(self, token_list):
        re_list = []
        for token in token_list:
            re_list.append(token.lower())
        return " ".join(re_list)

if __name__ == '__main__':
    pass

