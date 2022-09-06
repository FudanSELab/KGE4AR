# !/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
from queue import Queue
from threading import Thread
from milvus import Milvus
from py2neo import Graph
from sklearn import preprocessing



class InsertMilvus(Thread):
    def __init__(self, file_queue, thread_name, filter_data_dic):
        Thread.__init__(self, name=thread_name)
        self.file_queue = file_queue
        self.milvus = Milvus(host='10.176.34.89', port='19530')

        self.graph = Graph("bolt://10.176.64.33:9123", user="neo4j", password="fdsefdse")
        # self.graph = Graph("bolt://10.176.64.33:5687", user="neo4j", password="fdsefdse")
        self.collection_name = "migration_small_test_without_functionality"
        self.count = 0
        self.filter_data_dic = filter_data_dic
    def run(self):
        while self.file_queue.empty() == False:
            file_name = self.file_queue.get()
            self.load_data_dict_from_tsv_file(file_name)

    def insert_into_collection(self, collection, tag, ids, vectors, file_name):
        try:
            self.milvus.insert(collection_name=collection, records=vectors, ids=ids, partition_tag=tag)
            print("insert success: ", collection, " ", tag, ", num: ", len(ids), " thread name: ", self.name, " file name: ", file_name, len(ids), len(vectors))
        except BaseException as e:
            print("------------------------------------")
            print(e)
            print("insert error")
            print("------------------------------------")

    def load_data_dict_from_tsv_file(self, path, batch=5000):
        package_ids = []
        package_vectors = []
        class_ids = []
        class_vectors = []
        method_ids = []
        method_vectors = []
        library_ids = []
        library_vectors = []
        parameter_ids = []
        parameter_vectors = []
        return_value_ids = []
        return_value_vectors = []
        concept_ids = []
        concept_vectors = []
        method_desc_include_functionality_vectors = []
        method_desc_include_functionality_ids = []
        method_name_include_functionality_vectors = []
        method_name_include_functionality_ids = []
        func_verb_vectors = []
        func_verb_ids = []

        with open(path) as f:
            for line in f:
                try:
                    line_list = line.split()
                    # id = int(line_list[0])
                    # del line_list[0]
                    # re = self.__filter_from_file(id)
                    id = int(line_list[0])
                    del line_list[0]
                    re = self.__filter_from_neo4j(id)
                except BaseException as e:
                    print("------------------------------------")
                    print(e)
                    print(line_list)
                    print("process error")
                    print("------------------------------------")
                    continue
                if re == 1:
                    package_ids.append(id)
                    for i in range(len(line_list)):
                        line_list[i] = float(line_list[i])
                    package_vectors.append(line_list)

                    if len(package_ids) == batch:
                        package_vectors = self.__normalizer(package_vectors)
                        self.insert_into_collection(self.collection_name, 'package', package_ids, package_vectors, path)
                        package_ids = []
                        package_vectors = []
                if re == 2:
                    class_ids.append(id)
                    for i in range(len(line_list)):
                        line_list[i] = float(line_list[i])
                    class_vectors.append(line_list)
                    if len(class_ids) == batch:
                        class_vectors = self.__normalizer(class_vectors)
                        self.insert_into_collection(self.collection_name, 'class', class_ids, class_vectors, path)
                        class_ids = []
                        class_vectors = []
                if re == 3:
                    method_ids.append(id)
                    for i in range(len(line_list)):
                        line_list[i] = float(line_list[i])
                    method_vectors.append(line_list)
                    if len(method_ids) == batch:
                        method_vectors = self.__normalizer(method_vectors)
                        self.insert_into_collection(self.collection_name, 'method', method_ids, method_vectors, path)
                        method_ids = []
                        method_vectors = []
                if re == 4:
                    library_ids.append(id)
                    for i in range(len(line_list)):
                        line_list[i] = float(line_list[i])
                    library_vectors.append(line_list)
                    if len(library_ids) == batch:
                        library_vectors = self.__normalizer(library_vectors)
                        self.insert_into_collection(self.collection_name, 'library', library_ids, library_vectors, path)
                        library_ids = []
                        library_vectors = []
                if re == 5:
                    parameter_ids.append(id)
                    for i in range(len(line_list)):
                        line_list[i] = float(line_list[i])
                    parameter_vectors.append(line_list)
                    if len(parameter_ids) == batch:
                        parameter_vectors = self.__normalizer(parameter_vectors)
                        self.insert_into_collection(self.collection_name, 'parameter', parameter_ids, parameter_vectors, path)
                        parameter_ids = []
                        parameter_vectors = []
                if re == 6:
                    return_value_ids.append(id)
                    for i in range(len(line_list)):
                        line_list[i] = float(line_list[i])
                    return_value_vectors.append(line_list)
                    if len(return_value_ids) == batch:
                        return_value_vectors = self.__normalizer(return_value_vectors)
                        self.insert_into_collection(self.collection_name, 'return_value', return_value_ids, return_value_vectors, path)
                        return_value_ids = []
                        return_value_vectors = []
                if re == 7:
                    concept_ids.append(id)
                    for i in range(len(line_list)):
                        line_list[i] = float(line_list[i])
                    concept_vectors.append(line_list)
                    if len(concept_ids) == batch:
                        concept_vectors = self.__normalizer(concept_vectors)
                        self.insert_into_collection(self.collection_name, 'concept', concept_ids, concept_vectors, path)
                        concept_ids = []
                        concept_vectors = []
                if re == 8:
                    method_desc_include_functionality_ids.append(id)
                    for i in range(len(line_list)):
                        line_list[i] = float(line_list[i])
                    method_desc_include_functionality_vectors.append(line_list)
                    if len(method_desc_include_functionality_ids) == batch:
                        method_desc_include_functionality_vectors = self.__normalizer(method_desc_include_functionality_vectors)
                        self.insert_into_collection(self.collection_name, 'method_desc_include_functionality', method_desc_include_functionality_ids, method_desc_include_functionality_vectors, path)
                        method_desc_include_functionality_ids = []
                        method_desc_include_functionality_vectors = []
                if re == 9:
                    method_name_include_functionality_ids.append(id)
                    for i in range(len(line_list)):
                        line_list[i] = float(line_list[i])
                    method_name_include_functionality_vectors.append(line_list)
                    if len(method_name_include_functionality_ids) == batch:
                        method_name_include_functionality_vectors = self.__normalizer(method_name_include_functionality_vectors)
                        self.insert_into_collection(self.collection_name, 'method_name_include_functionality', method_name_include_functionality_ids, method_name_include_functionality_vectors, path)
                        method_name_include_functionality_ids = []
                        method_name_include_functionality_vectors = []
                if re == 10:
                    func_verb_ids.append(id)
                    for i in range(len(line_list)):
                        line_list[i] = float(line_list[i])
                    func_verb_vectors.append(line_list)
                    if len(func_verb_ids) == batch:
                        func_verb_vectors = self.__normalizer(func_verb_vectors)
                        self.insert_into_collection(self.collection_name, 'func_verb', func_verb_ids, func_verb_vectors, path)
                        func_verb_ids = []
                        func_verb_vectors = []



        if len(library_ids) != 0:
            library_vectors = self.__normalizer(library_vectors)
            self.insert_into_collection(self.collection_name, 'library', library_ids, library_vectors, path)
        if len(package_ids) != 0:
            package_vectors = self.__normalizer(package_vectors)
            self.insert_into_collection(self.collection_name, 'package', package_ids, package_vectors, path)
        if len(class_ids) != 0:
            class_vectors = self.__normalizer(class_vectors)
            self.insert_into_collection(self.collection_name, 'class', class_ids, class_vectors, path)
        if len(method_ids) != 0:
            method_vectors = self.__normalizer(method_vectors)
            self.insert_into_collection(self.collection_name, 'method', method_ids, method_vectors, path)
        if len(parameter_ids) != 0:
            parameter_vectors = self.__normalizer(parameter_vectors)
            self.insert_into_collection(self.collection_name, 'parameter', parameter_ids, parameter_vectors, path)
        if len(return_value_ids) != 0:
            return_value_vectors = self.__normalizer(return_value_vectors)
            self.insert_into_collection(self.collection_name, 'return_value', return_value_ids, return_value_vectors, path)
        if len(concept_ids) != 0:
            concept_vectors = self.__normalizer(concept_vectors)
            self.insert_into_collection(self.collection_name, 'concept', concept_ids, concept_vectors, path)
        if len(method_desc_include_functionality_ids) != 0:
            method_desc_include_functionality_vectors = self.__normalizer(method_desc_include_functionality_vectors)
            self.insert_into_collection(self.collection_name, 'method_desc_include_functionality', method_desc_include_functionality_ids, method_desc_include_functionality_vectors, path)
        if len(method_name_include_functionality_ids) != 0:
            method_name_include_functionality_vectors = self.__normalizer(method_name_include_functionality_vectors)
            self.insert_into_collection(self.collection_name, 'method_name_include_functionality', method_name_include_functionality_ids, method_name_include_functionality_vectors, path)
        if len(func_verb_ids) != 0:
            func_verb_vectors = self.__normalizer(func_verb_vectors)
            self.insert_into_collection(self.collection_name, 'func_verb', func_verb_ids, func_verb_vectors, path)

        print("file_ok:", path)

    def __filter_from_file(self, identity):
        index = self.filter_data_dic.get(str(identity), -1)

        return index

    def __filter_from_neo4j(self, idendity):
        try:
            cypher = 'match(n) where id(n) = {} return n'.format(idendity)
            result = [i['n'] for i in self.graph.run(cypher).data()]
            result = result[0]
            labels = str(result.labels)
            if 'package' in labels:
                return 1
            if ('class' in labels and 'field_of_class' not in labels) or 'interface' in labels:
                return 2
            if 'method' in labels and 'method_' not in labels:
                return 3
            if 'library' in labels:
                return 4
            if 'parameter' in labels:
                return 5
            if 'return_value' in labels:
                return 6
            if 'concept' in labels:
                return 7
            if 'method_desc_include_functionality' in labels:
                return 8
            if 'method_name_include_functionality' in labels:
                return 9
            if 'funcVerb' in labels:
                return 10

            return 0
        except BaseException as e:
            self.count = self.count + 1
            print(e)
            print("filter error", self.count)
            return 0

    def __normalizer(self, vertor_list, type='l2'):
        result = []
        vector_list = preprocessing.normalize(vertor_list, type)
        for vector in vector_list:
            result.append(list(vector))
        return result



if __name__ == '__main__':

    file_queue = Queue()
    file_name_list = []


    # file = "filter_data_big.json"

    # with open(file, encoding="utf-8") as f:
    #     filter_data_dic = json.load(f)
    filter_data_dic = {}

    # for i in range(8):
    #     file_name_list.append("entity_embeddings_apikg_817_finetune829_7_" + str(i+1) + ".tsv")
    # for i in range(8):
    #     file_name_list.append("entity_embeddings_apikg_817_finetune829_5_" + str(i+1) + ".tsv")
    # for i in range(8):
    #     file_name_list.append("entity_embeddings_apikg_817_finetune829_8_" + str(i+1) + ".tsv")
    # for i in range(8):
    #     file_name_list.append("entity_embeddings_apikg_817_finetune829_9_" + str(i+1) + ".tsv")


    file_name_list.append("entity_embeddings_apikg_test_826_without_functionality.tsv")


    for file_name in file_name_list:
        file_queue.put(file_name)

    for index, file_name in enumerate(file_name_list):
        im = InsertMilvus(file_queue, str(index), filter_data_dic)
        im.start()


