# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-----------------------------------------
@Author: zz
@Email: 21212010059@m.fudan.edu.cn
@Created: 2022/08/11
------------------------------------------
@Modify: 2022/08/11
------------------------------------------
@Description:
"""
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
            sentence = self.pipeline.special_characters_cleanup(sentence)  # 去除标点和数字
            token_list = self.pipeline.stop_words_removal(sentence.split())  # 去除停用词
            sentence = self.pipeline.split_camel_case(token_list)  # 驼峰拆分
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

    # def gene_id2multi_token_list(self, node: dict, file_name, library_id_list=None):
    #     map = {}
    #     for k, v in node.items():
    #         if library_id_list is None or v.get("library_id") in library_id_list:
    #             print("process", k)
    #             method_name = v.get("method_name", "")
    #             method_des = v.get("method_description", "")
    #             parameter_des = v.get("parameter_description", "")
    #             parameters = v.get("parameters", [])
    #             return_value_type_name = v.get("return_value_type_name", "")
    #             return_value_des = v.get("return_value_description", "")
    #
    #             name_list = []
    #             type_list = []
    #             for parameter in parameters:
    #                 if parameter.get("parameter_name", "") != "" and parameter.get("parameter_type", "") != "":
    #
    #                     name_list.append(parameter.get("parameter_name", ""))
    #                     type_list.append(parameter.get("parameter_type", ""))
    #
    #             temp = {}
    #             temp["beh"] = self.pipeline.extract_beh(method_name, method_des)
    #             temp["ps"], temp["pt"] = self.pipeline.extract_pt_ps(name_list, type_list, parameter_des, method_des)
    #             temp["rs"], temp["rt"] = self.pipeline.extract_rt_rs(return_value_type_name, return_value_des, method_des)
    #             map[str(k)] = temp
    #         else:
    #             print("hhhh")
    #     multi_token_list_file_name = os.path.join(DATA_DIR, "icpc_saner", file_name)
    #     FileUtil.write2json(multi_token_list_file_name, map)


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
