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
import os
import re
from nltk import stem
import en_core_web_sm
from definitions import DATA_DIR


class SentencePipeline():

    def __init__(self, name_keyword_list_file):
        path = os.path.join(DATA_DIR, "icpc_saner", name_keyword_list_file)
        with open(path) as f:
            self.name_keyword_list = eval(f.read())
        self.nlp = en_core_web_sm.load()
        self.stemmer = stem.LancasterStemmer()

    def extract_beh(self, name, des):
        name_word_list = self.text_preprocess(name)
        des_word_list = self.text_preprocess(des)

        return list(set(name_word_list).union(set(des_word_list).intersection(set(self.name_keyword_list))))

    def extract_pt_ps(self, name_list, type_list, para_des, method_des):
        ps_list = []
        pt_list = []
        para_des_tree = self.nlp(para_des)
        method_des_tree = self.nlp(method_des)

        para_des_token = para_des.split()
        para_des_token = self.lemmatization(para_des_token)
        para_des_token = self.lower_token(para_des_token)
        for type in type_list:
            if self.stemmer.stem(type.lower()) in para_des_token:
                pt_list.append([self.stemmer.stem(type.lower())])
            else:
                pt_list.append([])

        for name in name_list:
            flag = True
            name_word_list = [self.stemmer.stem(name)]
            name_word_list = self.lower_token(name_word_list)
            for word in para_des_tree:
                if self.stemmer.stem(word.text.lower()) == name_word_list[0]:
                    ps_list.append(name_word_list + [self.stemmer.stem(word.text.lower())] + [self.stemmer.stem(word.head.text.lower())])
                    flag = False
                    break
            if not flag:
                continue
            for word in method_des_tree:
                if self.stemmer.stem(word.text.lower()) == name_word_list[0]:
                    ps_list.append(name_word_list + [self.stemmer.stem(word.text.lower())] + [self.stemmer.stem(word.head.text.lower())])
                    flag = False
                    break
            if not flag:
                continue
            for word in para_des_tree:
                if word.pos_ == "NOUN" or word.pos_ == "VERB":
                    ps_list.append(name_word_list + [self.stemmer.stem(word.text.lower())])
                    flag = False
                    break
            if not flag:
                continue
            for word in method_des_tree:
                if word.pos_ == "NOUN" or word.pos_ == "VERB":
                    ps_list.append(name_word_list + [self.stemmer.stem(word.text.lower())])
                    flag = False
                    break
            if not flag:
                continue
            ps_list.append(name_word_list)

        return ps_list, pt_list

    def extract_rt_rs(self, type, return_value_des, method_des):
        rs_list = []
        rt_list = []
        return_value_des_tree = self.nlp(return_value_des)
        method_des_tree = self.nlp(method_des)

        return_value_des_token = return_value_des.split()
        return_value_des_token = self.lemmatization(return_value_des_token)
        return_value_des_token = self.lower_token(return_value_des_token)
        if type != "":
            if self.stemmer.stem(type.lower()) in return_value_des_token:
                rt_list.append([self.stemmer.stem(type.lower())])
            else:
                rt_list.append([])
        else:
            rt_list.append([])

        for word in return_value_des_tree:
            if self.stemmer.stem(word.text.lower()) == "return":
                rs_list.append([self.stemmer.stem(word.head.text.lower())])
                return rs_list, rt_list

        for word in method_des_tree:
            if self.stemmer.stem(word.text.lower()) == "return":
                rs_list.append([self.stemmer.stem(word.head.text.lower())])
                return rs_list, rt_list
        rs_list.append([])
        return rs_list, rt_list

    def text_preprocess(self, sentence):
        sentence = self.extract_first_sentence(sentence) #得到第一句话
        sentence = self.special_characters_cleanup(sentence)  #去除标点和数字
        token_list = self.stop_words_removal(sentence.split()) #去除停用词
        sentence = self.split_camel_case(token_list) # 驼峰拆分
        token_list = self.lower_token(sentence.split())
        token_list = self.lemmatization(token_list)

        return token_list

    def lower_token(self, token_list):
        re = [token.lower() for token in token_list]
        return re

    def extract_first_sentence(self, sentence):
        sentence = sentence[:sentence.find(".")]
        return sentence

    def stop_words_removal(self, token_list):
        stop_words = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll",
                      "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's",
                      'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs',
                      'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am',
                      'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does',
                      'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while',
                      'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during',
                      'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over',
                      'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how',
                      'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not',
                      'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don',
                      "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren',
                      "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn',
                      "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't",
                      'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren',
                      "weren't", 'won', "won't", 'wouldn', "wouldn't"]
        temp_list = []
        for token in token_list:
            if token not in stop_words:
                temp_list.append(token)

        return temp_list

    def special_characters_cleanup(self, sentence):
        sentence = sentence.strip()
        return re.sub('[0-9’!"#$%&\'()*+,-./:;<=>?@，。?★、…【】《》？“”‘’！[\\]^_`{|}~\s]+', " ", sentence)

    def _is_camel_case_boundary(self, prev, char, next):
        if prev.isdigit():
            return not char.isdigit()
        if char.isupper():
            return next.islower() or prev.isalpha() and not prev.isupper()
        return char.isdigit()

    def split_camel_case(self, token_list):
        result_list = []
        string_list = token_list
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

    def lemmatization(self, token_list):
        re_list = []
        for token in token_list:
            re_list.append(self.stemmer.stem(token))
        return re_list

    def lower_and_to_string(self, token_list):
        re_list = []
        for token in token_list:
            re_list.append(token.lower())
        return " ".join(re_list)


if __name__ == '__main__':

    pass


