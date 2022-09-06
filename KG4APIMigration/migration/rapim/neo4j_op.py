# !/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from threading import Thread
from py2neo import Graph
from definitions import DATA_DIR
from migration.util.file_util import FileUtil


class QueryData(Thread):

    def __init__(self, start_end_queue, thread_name, graph):
        Thread.__init__(self, name=thread_name)
        self.start_end_queue = start_end_queue
        self.graph = graph
        self.batch = 1000

    def run(self):
        while self.start_end_queue.empty() == False:
            start_end = self.start_end_queue.get()
            self.query_data(start_end)

    def query_data(self, start_end):
        result = {}
        batch_num = (start_end[1] - start_end[0] + 1) // self.batch
        if (start_end[1] - start_end[0] + 1) % self.batch != 0:
            batch_num = batch_num + 1
        print(self.name, " start", "batch num", batch_num)
        for i in range(batch_num):
            print(self.name, " start", "batch num", batch_num, "now process", i)
            start = start_end[0] + i * self.batch
            end = min(start_end[0] + (i+1) * self.batch, start_end[1])

            cypher = "match(n:method) where id(n)>={} and id(n)<={} return n, id(n)".format(start, end)
            data_list = self.graph.run(cypher).data()
            for data in data_list:
                id = data["id(n)"]
                try:
                    method = dict(data["n"])
                except BaseException as e:
                    method = {}
                method_description = method.get("description", "")
                method_name = method.get("name", "")
                library_id = method.get("library_id", -1)
                parameter_signature = method_name[method_name.find("("):].replace("(", "").replace(")", "")
                method_name = method_name[:method_name.find("(")]
                dic = result.get(id, {})
                dic["library_id"] = library_id
                dic["method_name"] = method_name
                dic["method_description"] = method_description
                dic["parameter_signature"] = parameter_signature
                dic["parameter_description"] = ""
                dic["parameters"] = []
                result[id] = dic

            cypher = "match(n:method)-[:has_parameter]-(p) where id(n)>={} and id(n)<={} return id(n), p".format(start, end)
            data_list = self.graph.run(cypher).data()
            temp = {}
            para_temp = {}
            for data in data_list:
                id = data["id(n)"]
                try:
                    parameter = dict(data["p"])
                except BaseException as e:
                    parameter = {}
                parameter_description_list = temp.get(id, [])
                parameters_list = para_temp.get(id, [])
                parameter_description = parameter.get("description", "")
                parameter_name = parameter.get("name", "")
                parameter_type = parameter.get("type", "")
                if parameter_name != "" and parameter_type != "":
                    parameters_list.append({"parameter_name": parameter_name, "parameter_type": parameter_type})
                if parameter_description != "":
                    parameter_description_list.append(parameter_description)
                temp[id] = parameter_description_list
                para_temp[id] = parameters_list
            for k, v in temp.items():
                dic = result.get(k, {})
                dic["parameter_description"] = " ".join(v)
                result[k] = dic
            for k, v in para_temp.items():
                dic = result.get(k, {})
                dic["parameters"] = v
                result[k] = dic

            cypher = "match (n:method)-[:belong_to]-()-[:exists_in]-(p) where id(n)>={} and id(n)<={} return id(n), p".format(start, end)
            data_list = self.graph.run(cypher).data()
            for data in data_list:
                id = data["id(n)"]
                try:
                    package = dict(data["p"])
                except BaseException as e:
                    package = {}
                package_name = package.get("qualified_name", "")
                dic = result.get(id, {})
                dic["package_name"] = package_name
                result[id] = dic

            cypher = "match (t)-[:return_value_type_of]-(r)-[:has_return_value]-(n:method) where id(n)>={} and id(n)<={} return id(n), r, n, t, id(t)".format(start, end)
            data_list = self.graph.run(cypher).data()
            for data in data_list:
                id = data["id(n)"]
                id_t = data["id(t)"]
                try:
                    return_value_type = dict(data["t"])
                except BaseException as e:
                    return_value_type = {}
                try:
                    return_value = dict(data["r"])
                except BaseException as e:
                    return_value = {}
                return_value_description = return_value.get("description", "")
                return_value_type_name = return_value_type.get("name", "")
                return_value_type_id = id_t
                dic = result.get(id, {})
                dic["return_value_description"] = return_value_description
                dic["return_value_type_id"] = return_value_type_id
                dic["return_value_type_name"] = return_value_type_name
                result[id] = dic

        print(str(self.name), start_end, len(result.keys()))
        file_name = os.path.join(DATA_DIR, "icpc_saner", str(self.name)+".json")
        FileUtil.write2json(file_name, result)

    @staticmethod
    def merge(dic_list, file_name):
        res_dic = dic_list[0]

        for index, dic in enumerate(dic_list):
            if index == 0:
                continue
            res_dic.update(dic)
        file_name = os.path.join(DATA_DIR, "icpc_saner", file_name)
        print(len(res_dic.keys()))
        FileUtil.write2json(file_name, res_dic)


