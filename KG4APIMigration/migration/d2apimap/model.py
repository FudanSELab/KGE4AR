# !/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
import os
import gensim.models
from definitions import DATA_DIR
from migration.d2apimap.sentence_pipeline import SentencePipeline
from migration.util.file_util import FileUtil


class Word2VectorModel():

    def __init__(self, pipeline: SentencePipeline=None):
        self.model = None
        self.pipeline = pipeline

    def gene_model(self, file2property, model_name, min_count, window, vector_size):
        texts = []
        sentence_list = []
        for k, v in file2property.items():
            print("process file", k)
            if "method" in k:
                with open(os.path.join(DATA_DIR, "icpc_saner", v), encoding='utf-8') as f:
                    f_csv = csv.reader(f)
                    for line in f_csv:
                        method_description = line[2]
                        method_name = line[1]
                        if method_description != "" or method_name != "":
                            sentence_list.append(method_description + " " + method_name)
            if "return_value" in k:
                data_list = FileUtil.load_data_list(os.path.join(DATA_DIR, "icpc_saner", v))
                for data in data_list:
                    return_value_description = data.get("description", "")
                    if return_value_description != "":
                        sentence_list.append(return_value_description)
            if "parameter" in k:
                data_list = FileUtil.load_data_list(os.path.join(DATA_DIR, "icpc_saner", v))
                for data in data_list:
                    parameter_description = data.get("description", "")
                    if parameter_description != "":
                        sentence_list.append(parameter_description)
        print("sentence len", len(sentence_list))
        for sentence in sentence_list:
            sentence = self.pipeline.special_characters_cleanup(sentence)
            token_list = self.pipeline.stop_words_removal(sentence.split())
            sentence = self.pipeline.split_camel_case(token_list)
            sentence = self.pipeline.lower_and_to_string(sentence.split())
            token_list = self.pipeline.lemmatization(sentence.split())
            texts.append(token_list)

        model = gensim.models.Word2Vec(texts, min_count=min_count, window=window, vector_size=vector_size, epochs=10)
        path = os.path.join(DATA_DIR, "icpc_saner", model_name)
        model.save(path)

    def gene_name_token_list(self, file, file_name):
        li = set([])
        file = os.path.join(DATA_DIR, "icpc_saner", file)
        with open(file, encoding='utf-8') as f:
            f_csv = csv.reader(f)
            for line in f_csv:
                method_name = line[1]
                if method_name != "":
                    li.update(self.pipeline.text_preprocess(method_name[:method_name.find("(")]))
        file = os.path.join(DATA_DIR, "icpc_saner", file_name)
        print(len(li))
        with open(file, 'w', encoding='utf-8') as f:
            f.write(str(li))
        print("gene ", file, "success")

    def load_model(self, model_name):
        path = os.path.join(DATA_DIR, "icpc_saner", model_name)
        self.model = gensim.models.Word2Vec.load(path)

    def gene_vector(self, text):
        try:
            return self.model.wv[text]
        except BaseException as e:
            # print("can not find {} in word2vector_test model".format(text))
            return None

if __name__ == '__main__':

    pass
