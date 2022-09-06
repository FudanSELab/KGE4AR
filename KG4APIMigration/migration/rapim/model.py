# !/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import os
from functools import lru_cache

from gensim import corpora, models
from gensim.models import TfidfModel
from definitions import DATA_DIR
from migration.util.file_util import FileUtil


class TfIdfModel():

    def __init__(self, pipeline=None):
        self.model = None
        self.token2id = None
        self.pipeline = pipeline

    def gene_model_and_dictionary(self, file2property, model_name, dictionary_name):
        texts = []
        for k, v in file2property.items():
            print("process file", k)
            if "method" in k:
                with open(os.path.join(DATA_DIR, "icpc_saner", v), encoding='utf-8') as f:
                    f_csv = csv.reader(f)
                    for line in f_csv:
                        method_name = line[1]
                        if method_name != "":
                            method_name = self.pipeline.ie(method_name)
                            texts.append(method_name.split())
                        method_description = line[2]
                        if method_description != "":
                            method_description = self.pipeline.tpp(method_description)
                            texts.append(method_description.split())

            if "return_value" in k:
                data_list = FileUtil.load_data_list(os.path.join(DATA_DIR, "icpc_saner", v))
                for data in data_list:
                    return_value_description = data.get("description", "")
                    if return_value_description != "":
                        return_value_description = self.pipeline.tpp(return_value_description)
                        texts.append(return_value_description.split())

            if "parameter" in k:
                data_list = FileUtil.load_data_list(os.path.join(DATA_DIR, "icpc_saner", v))
                for data in data_list:
                    parameter_description = data.get("description", "")
                    if parameter_description != "":
                        parameter_description = self.pipeline.tpp(parameter_description)
                        texts.append(parameter_description.split())

        dictionary = corpora.Dictionary(texts)
        dictionary_path = os.path.join(DATA_DIR, "icpc_saner", dictionary_name)
        with open(dictionary_path, 'w', encoding='utf-8') as f:
            f.write(str(dictionary.token2id))
        corpus = [dictionary.doc2bow(text) for text in texts]
        tf_idf_model = TfidfModel(corpus, normalize=False)
        model_path = os.path.join(DATA_DIR, "icpc_saner", model_name)
        models.TfidfModel.save(tf_idf_model, model_path)

    def load_model_and_dictionary(self, model_name, dictionary_name):
        model_path = os.path.join(DATA_DIR, "icpc_saner", model_name)
        self.model = models.TfidfModel.load(model_path)
        dictionary_path = os.path.join(DATA_DIR, "icpc_saner", dictionary_name)
        with open(dictionary_path, 'r', encoding='utf-8') as f:
            self.token2id = eval(f.read())


    @lru_cache(maxsize=10000)
    def gene_vector(self, text, type):
        if type == "ie":
            text = self.pipeline.ie(text)
        else:
            text = self.pipeline.tpp(text)
        text = text.split()
        vector = [0 for i in range(len(self.token2id))]
        token2tf = {}
        for text_ in text:
            token2tf[text_] = token2tf.get(text_, 0) + 1
        for token, tf in token2tf.items():
            try:
                id = self.token2id[token]
                tf = token2tf[token]
                vector[id] = self.model[[(int(id), int(tf))]][0][1]
            except BaseException as e:
                pass
        return vector

if __name__ == '__main__':
    pass

