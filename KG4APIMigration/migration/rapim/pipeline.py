# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-----------------------------------------
@Author: zz
@Email: 21212010059@m.fudan.edu.cn
@Created: 2022/08/08
------------------------------------------
@Modify: 2022/08/08
------------------------------------------
@Description:
"""
import json
import time
import requests
import numpy as np
from elasticsearch import Elasticsearch
from migration.calculator.base import CombineSimResultCollection, SimResult
from migration.rapim.sentence_pipeline import SentencePipeline
from migration.util.neo4j_util import Neo4jUtil


class RApiM():

    def __init__(self, library_method_dic: dict, model, graph, graph_util: Neo4jUtil, filter, library_method_info_dic: dict=None):
        self.library_method_dic = library_method_dic
        self.model = model
        self.es = Elasticsearch([{"host": "10.176.34.89", "port": 8200}])
        self.sp = SentencePipeline()
        self.filter = filter
        self.graph = graph
        self.graph_util = graph_util
        self.library_method_info = library_method_info_dic

    def get_node_info(self, node_id):
        if self.library_method_info is not None:
            if self.library_method_info.get(str(node_id), None) is not None:
                return self.library_method_info.get(str(node_id))

        try:
            re = {
                "method_name": "",
                "method_description": "",
                "parameter_signature": "",
                "parameter_description": "",
                "method_qualified_name": "",
                "parameters": [],
                "package_name": "",
                "return_value_description": "",
                "return_value_type_id": -1,
                "return_value_type_name": ""
            }

            cypher = "match (rt)<-[:return_value_type_of]-(r:return_value)<-[:has_return_value]-(m:method)-[:belong_to]->(c)-[:exists_in]->" \
                     "(p:packages) where id(m)={} return rt, r, m, p, id(rt)".format(node_id)
            data_list = self.graph.run(cypher).data()
            for data in data_list:
                rt = dict(data["rt"])
                r = dict(data["r"])
                m = dict(data["m"])
                p = dict(data["p"])

                method_description = m.get("description", "")
                method_name = m.get("name", "")
                method_qualified_name = m.get("qualified_name", "")
                parameter_signature = method_name[method_name.find("("):].replace("(", "").replace(")", "")
                method_name = method_name[:method_name.find("(")]
                package_name = p.get("qualified_name", "")
                return_value_description = r.get("description", "")
                return_value_type_name = rt.get("name", "")
                return_value_type_id = data["id(rt)"]

                re["method_name"] = method_name
                re["method_qualified_name"] = method_qualified_name
                re["method_description"] = method_description
                re["package_name"] = package_name
                re["return_value_description"] = return_value_description
                re["return_value_type_name"] = return_value_type_name
                re["return_value_type_id"] = return_value_type_id
                re["parameter_signature"] = parameter_signature

            cypher = "match(m:method)-[:has_parameter]-(p) where id(m)={} return p".format(node_id)
            data_list = self.graph.run(cypher).data()
            parameter_description_list = []
            for data in data_list:
                p = dict(data["p"])
                parameter_description = p.get("description", "")
                parameter_name = p.get("name", "")
                parameter_type = p.get("type", "")
                if parameter_description != "":
                   parameter_description_list.append(parameter_description)
                if parameter_name != "" and parameter_type != "":
                    re["parameters"].append({"parameter_name": parameter_name, "parameter_type": parameter_type})

            re["parameter_description"] = " ".join(parameter_description_list)
            return re
        except BaseException as e:
            print(e)
            return None

    def run_es(self, start_api_id, rerank_topN=3000, type="test"):
        combine_sim_collection = CombineSimResultCollection(start_id=start_api_id)
        node_id_list = []

        node_data_dic: dict = self.get_node_info(int(start_api_id))
        node_name = node_data_dic.get("method_qualified_name", "")
        node_name = self.sp.special_characters_cleanup(node_name)
        node_name = self.sp.split_camel_case(node_name).lower()
        node_description = node_data_dic.get("method_description", "")
        node_description = self.sp.special_characters_cleanup(node_description)
        node_description = self.sp.split_camel_case(node_description).lower()
        node_name_description = node_name + " " + node_description
        body = {
            "query": {
                "match": {
                    "content": node_name_description
                }
            },
            "size": rerank_topN
        }

        hits_list = self.es.search(index='api_migration_name_description_{}'.format(type), body=body, size=rerank_topN)["hits"]["hits"]
        id2score = {}

        for hits in hits_list:
            id = hits.get("_source", {}).get("id", -1)
            score = hits.get("_score", 0)
            if id != -1:
                node_id_list.append(id)
                id2score[str(id)] = score
        if start_api_id in node_id_list:
            node_id_list.remove(start_api_id)
        print("before filter: ", len(node_id_list))

        node_id_list = self.filter.filter_for_icpc(start_api_id=start_api_id, id_list=node_id_list)

        print("after filter: ", len(node_id_list))

        for id in node_id_list:
            sr = SimResult(start_api_id, id, float(id2score[str(id)]))
            combine_sim_collection.add_sim_result("model", sr)
        return combine_sim_collection

    def run(self, start_api_id, target_api_id=None, rerank_topN=3000, type="test"):
        combine_sim_collection = CombineSimResultCollection(start_id=start_api_id)
        node_id_list = []
        if target_api_id is not None:
            library_id = self.graph_util.get_library_id_by_node_id(int(target_api_id))
            if library_id != -1:
                node_id_list = self.library_method_dic.get(str(library_id))
                if len(node_id_list) >4000:
                    node_id_list = node_id_list[:500]
        else:
            node_data_dic: dict = self.get_node_info(int(start_api_id))
            node_qualified_name = node_data_dic.get("method_qualified_name", "")
            node_qualified_name = self.sp.special_characters_cleanup(node_qualified_name)
            node_qualified_name = self.sp.split_camel_case(node_qualified_name).lower()
            node_description = node_data_dic.get("method_description", "")
            node_description = self.sp.special_characters_cleanup(node_description)
            node_description = self.sp.split_camel_case(node_description).lower()
            node_name_description = node_qualified_name + " " + node_description
            print("content", node_name_description)
            body = {
                "query": {
                    "match": {
                        "content": node_name_description
                    }
                },
                "size": rerank_topN
            }

            hits_list = self.es.search(index='api_migration_name_description_{}'.format(type), body=body, size=rerank_topN)["hits"]["hits"]

            for hits in hits_list:
                id = hits.get("_source", {}).get("id", -1)
                if id != -1:
                    node_id_list.append(id)
            if start_api_id in node_id_list:
                node_id_list.remove(start_api_id)

        print("before filter: ", len(node_id_list))
        if target_api_id is None:
            node_id_list = self.filter.filter_for_icpc(start_api_id=start_api_id, id_list=node_id_list)
        if len(node_id_list) == 0:
            node_data_dic: dict = self.get_node_info(int(start_api_id))
            node_qualified_name = node_data_dic.get("method_qualified_name", "")
            node_qualified_name = self.sp.special_characters_cleanup(node_qualified_name)
            node_qualified_name = self.sp.split_camel_case(node_qualified_name).lower()
            node_description = node_data_dic.get("method_description", "")
            node_description = self.sp.special_characters_cleanup(node_description)
            node_description = self.sp.split_camel_case(node_description).lower()
            node_name_description = node_qualified_name + " " + node_description
            print("content", node_name_description)
            body = {
                "query": {
                    "match": {
                        "content": node_name_description
                    }
                },
                "size": rerank_topN*4
            }

            hits_list = self.es.search(index='api_migration_name_description_{}'.format(type), body=body, size=rerank_topN*4)["hits"]["hits"]

            for hits in hits_list:
                id = hits.get("_source", {}).get("id", -1)
                if id != -1:
                    node_id_list.append(id)
            if start_api_id in node_id_list:
                node_id_list.remove(start_api_id)
            if target_api_id is None:
                node_id_list = self.filter.filter_for_icpc(start_api_id=start_api_id, id_list=node_id_list)
        print("after filter: ", len(node_id_list))
        retrieve_result_list = []
        id_pair_list = []

        for node_id in node_id_list:

            retrieve_result = self.retrieve(start_api_id, node_id)
            retrieve_result_list.append(retrieve_result)
            id_pair_list.append([start_api_id, node_id])
        print("after retrieve: ", len(id_pair_list))
        rerank_result_list = self.rerank(retrieve_result_list, id_pair_list)
        rerank_result_list = rerank_result_list[:rerank_topN]
        print("after rerank: ", len(id_pair_list))

        for rerank_result in rerank_result_list:
            sr = SimResult(rerank_result["method_1"], rerank_result["method_2"], float(rerank_result["Scored Probabilities"]), rerank_result["extra"])
            combine_sim_collection.add_sim_result("model", sr)
        return combine_sim_collection

    def retrieve(self, id1, id2):
        node1_info = self.get_node_info(int(id1))
        node2_info = self.get_node_info(int(id2))
        query_body = {
            "1": 0.0,
            "2": 0.0,
            "3": 0.0,
            "4": 0.0,
            "5": 0.0,
            "6": 0.0,
            "7": 0.0,
            "8": 0.0,
            "output": 0
        }
        if node1_info is not None and node2_info is not None:
            method_description1 = node1_info.get("method_description", "")
            method_description2 = node2_info.get("method_description", "")
            if method_description1 != "" and method_description2 != "":
                method_description1_vector = self.model.gene_vector(method_description1, "tpp")
                method_description2_vector = self.model.gene_vector(method_description2, "tpp")
                query_body["1"] = self.calculate_vector_distance(method_description1_vector, method_description2_vector)
            else:
                query_body["1"] = 0.0

            return_value_type_description1 = node1_info.get("return_value_type_description", "")
            return_value_type_description2 = node2_info.get("return_value_type_description", "")
            if return_value_type_description1 != "" and return_value_type_description2 != "":
                return_value_type_description1_vector = self.model.gene_vector(return_value_type_description1, "tpp")
                return_value_type_description2_vector = self.model.gene_vector(return_value_type_description2, "tpp")
                query_body["2"] = self.calculate_vector_distance(return_value_type_description1_vector, return_value_type_description2_vector)
            else:
                query_body["2"] = 0.0

            parameter_description1 = node1_info.get("parameter_description", "")
            parameter_description2 = node2_info.get("parameter_description", "")
            if parameter_description1 != "" and parameter_description2 != "":
                parameter_description1_vector = self.model.gene_vector(parameter_description1, "tpp")
                parameter_description2_vector = self.model.gene_vector(parameter_description2, "tpp")
                query_body["3"] = self.calculate_vector_distance(parameter_description1_vector, parameter_description2_vector)
            else:
                query_body["3"] = 0.0

            parameter_signature1 = node1_info.get("parameter_signature", "")
            parameter_signature2 = node2_info.get("parameter_signature", "")
            if parameter_signature1 == parameter_signature2:
                query_body["4"] = 1.0
            else:
                query_body["4"] = 0.0

            method_name1 = node1_info.get("method_name", "")
            method_name2 = node2_info.get("method_name", "")
            if method_name1 != "" and method_name2 != "":
                method_name1_vector = self.model.gene_vector(method_name1, "ie")
                method_name2_vector = self.model.gene_vector(method_name2, "ie")
                query_body["5"] = self.calculate_vector_distance(method_name1_vector, method_name2_vector)
            else:
                query_body["5"] = 0.0

            return_value_type_id1 = node1_info.get("return_value_type_id", "")
            return_value_type_id2 = node2_info.get("return_value_type_id", "")
            if parameter_signature1 != "" and parameter_signature2 != "":
                if return_value_type_id1 == return_value_type_id2:
                    query_body["6"] = 1.0
                else:
                    query_body["6"] = 0.0
            else:
                query_body["6"] = 0.0

            parameter_num1 = len(node1_info.get("parameters", ""))
            parameter_num2 = len(node2_info.get("parameters", ""))
            if parameter_num1 == 0 and parameter_num2 == 0:
                query_body["7"] = 1
            else:
                if parameter_num1 != "" and parameter_num2 != "":
                    query_body["7"] = 1.0 - abs(parameter_num1 - parameter_num2) / (parameter_num1 + parameter_num2)
                else:
                    query_body["7"] = 0.0

            package_name1 = node1_info.get("package_name", "")
            package_name2 = node2_info.get("package_name", "")
            if package_name1 != "" and package_name2 != "":
                package_name1_vector = self.model.gene_vector(package_name1, "ie")
                package_name2_vector = self.model.gene_vector(package_name2, "ie")
                query_body["8"] = self.calculate_vector_distance(package_name1_vector, package_name2_vector)
            else:
                query_body["8"] = 0.0
            query_body["output"] = 0.0
            return query_body
        return query_body

    def rerank(self, retrieve_result_list, id_pair_list):
        data = {
            "Inputs": {
                "input1":
                    retrieve_result_list,
            },
            "GlobalParameters": {
            }
        }
        body = str.encode(json.dumps(data))
        url = 'https://ussouthcentral.services.azureml.net/workspaces/fd769a98302c4c5d88faec13f23806f4/services/c8bd65a25e0f4b11b09a2f3226262d3a/execute?api-version=2.0&format=swagger'
        api_key = 'J9RWXmUb14jvpWnfewsQam15EfCiKv2vaT+apVfr3Jzf7IfWWsOLoMCkYg5YTFJM3Ha8Ri8lzDYjv5Mr3eWivg=='
        headers = {'Content-Type': 'application/json', 'Authorization': ('Bearer ' + api_key)}
        response = requests.post(url, headers=headers, data=body)
        result = response.json()
        try:
            re = []
            for index, output in enumerate(result["Results"]["output1"]):
                re.append({"Scored Labels": output["Scored Labels"], "Scored Probabilities": output["Scored Probabilities"], "method_1": id_pair_list[index][0], "method_2": id_pair_list[index][1], "extra": retrieve_result_list[index]})
            re = sorted(re, key=lambda k: k['Scored Probabilities'], reverse=True)
            return re
        except BaseException as e:
            print(e)
            re = []
            for index, id_pair in enumerate(id_pair_list):
                re.append({"Scored Labels": "0", "Scored Probabilities": 0, "method_1": id_pair_list[index][0], "method_2": id_pair_list[index][1], "extra": retrieve_result_list[index]})
            return re

    def calculate_vector_distance(self, vector1, vector2):
        vector1 = np.array(vector1)
        vector2 = np.array(vector2)
        cos = vector1.dot(vector2) / (np.linalg.norm(vector1) * np.linalg.norm(vector2))

        return cos


if __name__ == '__main__':
    pass