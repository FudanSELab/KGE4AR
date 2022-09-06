# !/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
from elasticsearch import Elasticsearch
from scipy.optimize import linear_sum_assignment
from migration.calculator.base import CombineSimResultCollection, SimResult
from migration.d2apimap.model import Word2VectorModel
from migration.d2apimap.sentence_pipeline import SentencePipeline



class D2ApiMap():

    def __init__(self, library_method_dic: dict, model: Word2VectorModel, sentence_pipeline: SentencePipeline, graph, graph_util, filter, library_method_info_dic: dict=None):
        self.library_method_dic = library_method_dic
        self.model = model
        self.sentence_pipeline = sentence_pipeline
        self.wb = 1.4
        self.wp = 1.0
        self.wr = 0.3
        self.es = Elasticsearch([{"host": "10.176.34.89", "port": 8200}])
        self.filter = filter
        self.graph = graph
        self.graph_util = graph_util
        self.library_method_info_dic = library_method_info_dic

    def get_node_info(self, node_id):
        if self.library_method_info_dic is not None:
            if self.library_method_info_dic.get(str(node_id), None) is not None:
                return self.library_method_info_dic.get(str(node_id))
        try:
            re = {
                "method_name": "",
                "method_qualified_name": "",
                "method_description": "",
                "parameter_signature": "",
                "parameter_description": "",
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

    def run(self, start_api_id, target_api_id=None, rerank_topN=3000, type="test"):
        combine_sim_collection = CombineSimResultCollection(start_id=start_api_id)
        node_id_list = []

        if target_api_id is not None:
            library_id = self.graph_util.get_library_id_by_node_id(int(target_api_id))
            if library_id != -1:
                node_id_list = self.library_method_dic.get(str(library_id))
        else:
            node_data_dic: dict = self.get_node_info(int(start_api_id))
            node_name = node_data_dic.get("method_qualified_name", "")
            node_name = self.sentence_pipeline.special_characters_cleanup(node_name)
            node_name = self.sentence_pipeline.split_camel_case(node_name.split()).lower()
            node_description = node_data_dic.get("method_description", "")
            node_description = self.sentence_pipeline.special_characters_cleanup(node_description)
            node_description = self.sentence_pipeline.split_camel_case(node_description.split()).lower()
            node_name_description = node_name + " " + node_description
            body = {
                "query": {
                    "match": {
                        "content": node_name_description
                    }
                },
                "size": rerank_topN
            }
            print("query content", node_name_description)
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
        if len(node_id_list) ==0:
            node_data_dic: dict = self.get_node_info(int(start_api_id))
            node_name = node_data_dic.get("method_qualified_name", "")
            node_name = self.sentence_pipeline.special_characters_cleanup(node_name)
            node_name = self.sentence_pipeline.split_camel_case(node_name.split()).lower()
            node_description = node_data_dic.get("method_description", "")
            node_description = self.sentence_pipeline.special_characters_cleanup(node_description)
            node_description = self.sentence_pipeline.split_camel_case(node_description.split()).lower()
            node_name_description = node_name + " " + node_description
            body = {
                "query": {
                    "match": {
                        "content": node_name_description
                    }
                },
                "size": rerank_topN *4
            }
            print("query content", node_name_description)
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
        print("after rerank: ", len(rerank_result_list))
        for rerank_result in rerank_result_list:
            sr = SimResult(rerank_result["method_1"], rerank_result["method_2"], float(rerank_result["score"]), rerank_result["extra"])
            combine_sim_collection.add_sim_result("model", sr)
        return combine_sim_collection


    def retrieve(self, id1, id2):
        node_info = self.get_node_info(str(id1))
        method_name = node_info.get("method_name", "")
        method_des = node_info.get("method_description", "")
        parameter_des = node_info.get("parameter_description", "")
        parameters = node_info.get("parameters", [])
        return_value_type_name = node_info.get("return_value_type_name", "")
        return_value_des = node_info.get("return_value_description", "")
        name_list = []
        type_list = []
        for parameter in parameters:
            if parameter.get("parameter_name", "") != "" and parameter.get("parameter_type", "") != "":
                name_list.append(parameter.get("parameter_name", ""))
                type_list.append(parameter.get("parameter_type", ""))

        token_map1 = {}
        token_map1["beh"] = self.sentence_pipeline.extract_beh(method_name, method_des)
        token_map1["ps"], token_map1["pt"] = self.sentence_pipeline.extract_pt_ps(name_list, type_list, parameter_des, method_des)
        token_map1["rs"], token_map1["rt"] = self.sentence_pipeline.extract_rt_rs(return_value_type_name, return_value_des, method_des)

        node_info = self.get_node_info(str(id2))
        method_name = node_info.get("method_name", "")
        method_des = node_info.get("method_description", "")
        parameter_des = node_info.get("parameter_description", "")
        parameters = node_info.get("parameters", [])
        return_value_type_name = node_info.get("return_value_type_name", "")
        return_value_des = node_info.get("return_value_description", "")
        name_list = []
        type_list = []
        for parameter in parameters:
            if parameter.get("parameter_name", "") != "" and parameter.get("parameter_type", "") != "":
                name_list.append(parameter.get("parameter_name", ""))
                type_list.append(parameter.get("parameter_type", ""))

        token_map2 = {}
        token_map2["beh"] = self.sentence_pipeline.extract_beh(method_name, method_des)
        token_map2["ps"], token_map2["pt"] = self.sentence_pipeline.extract_pt_ps(name_list, type_list, parameter_des, method_des)
        token_map2["rs"], token_map2["rt"] = self.sentence_pipeline.extract_rt_rs(return_value_type_name, return_value_des, method_des)

        if token_map1 == {} or token_map2 == {}:
            return {"beh": 0, "ps_pt": 0, "rs_rt": 0}

        beh_token1 = token_map1.get("beh", [])
        ps_token1 = token_map1.get("ps", [])
        pt_token1 = token_map1.get("pt", [])
        rs_token1 = token_map1.get("rs", [])
        rt_token1 = token_map1.get("rt", [])

        beh_token2 = token_map2.get("beh", [])
        ps_token2 = token_map2.get("ps", [])
        pt_token2 = token_map2.get("pt", [])
        rs_token2 = token_map2.get("rs", [])
        rt_token2 = token_map2.get("rt", [])

        beh_vector1 = self.get_vector(beh_token1)
        beh_vector2 = self.get_vector(beh_token2)
        if beh_vector1 is None or beh_vector2 is None:
            beh = 0
        else:
            beh = self.calculate_vector_distance(beh_vector1, beh_vector2)

        if len(ps_token1) == 0 and len(ps_token2) == 0:
            ps_pt = 1
        elif len(ps_token1) != 0 and len(ps_token2) != 0:
            ps_pt = self.get_most_match_score(ps_token1, pt_token1, ps_token2, pt_token2)
        else:
            ps_pt = 0

        if len(rs_token1) == 0 and len(rs_token2) == 0:
            rs_rt = 1
        elif len(rs_token1) != 0 and len(rs_token2) != 0:
            rs_rt = self.get_most_match_score(rs_token1, rt_token1, rs_token2, rt_token2)
        else:
            rs_rt = 0

        return {"beh": beh, "ps_pt": ps_pt, "rs_rt": rs_rt}


    def get_most_match_score(self, s_token1, t_token1, s_token2, t_token2):
        s_vectors1 = []
        s_vectors2 = []
        s_matrix = []
        for s_token in s_token1:
            vector = self.get_vector(s_token)
            s_vectors1.append(vector)

        for s_token in s_token2:
            vector = self.get_vector(s_token)
            s_vectors2.append(vector)
        for i in range(len(s_vectors1)):
            temp = []
            for j in range(len(s_vectors2)):
                vector1 = s_vectors1[i]
                vector2 = s_vectors2[j]
                if vector1 is None or vector2 is None:
                    temp.append(0)
                else:
                    temp.append(self.calculate_vector_distance(vector1, vector2))
            s_matrix.append(temp)

        t_vectors1 = []
        t_vectors2 = []
        t_matrix = []
        for t_token in t_token1:
            vector = self.get_vector(t_token)
            t_vectors1.append(vector)

        for t_token in t_token2:
            vector = self.get_vector(t_token)
            t_vectors2.append(vector)
        for i in range(len(t_vectors1)):
            temp = []
            for j in range(len(t_vectors2)):
                vector1 = t_vectors1[i]
                vector2 = t_vectors2[j]
                if vector1 is None or vector2 is None:
                    temp.append(0)
                else:
                    temp.append(self.calculate_vector_distance(vector1, vector2))
            t_matrix.append(temp)

        return self.hungarian(s_matrix, t_matrix)


    def hungarian(self, ps_matrix, pt_matrix):
        for line in ps_matrix:
            for index, i in enumerate(line):
                line[index] = -i

        for line in pt_matrix:
            for index, i in enumerate(line):
                line[index] = -i
        ps_matrix = np.array(ps_matrix)
        pt_matrix = np.array(pt_matrix)

        ps_row_ind, ps_col_ind = linear_sum_assignment(ps_matrix)
        ps_matrix_score = -ps_matrix[ps_row_ind, ps_col_ind].sum()
        ps_count = 0
        for i in ps_matrix[ps_row_ind, ps_col_ind]:
            if i != 0:
                ps_count = ps_count + 1

        pt_row_ind, pt_col_ind = linear_sum_assignment(pt_matrix)
        pt_matrix_score = -pt_matrix[pt_row_ind, pt_col_ind].sum()
        pt_count = 0
        for i in pt_matrix[pt_row_ind, pt_col_ind]:
            if i != 0:
                pt_count = pt_count + 1
        if ps_matrix_score >= pt_matrix_score:
            if ps_count == 0:
                return 0
            return (ps_matrix_score + -pt_matrix[ps_row_ind, ps_col_ind].sum())/ps_count
        else:
            if pt_count == 0:
                return 0
            return (pt_matrix_score + -ps_matrix[pt_row_ind, pt_col_ind].sum())/pt_count

    def get_vector(self, token_list):
        vectors = []
        for token in token_list:
            vector = self.model.gene_vector(token)
            if vector is not None:
                vectors.append(vector)
        if vectors == []:
            return None
        vector = np.average(vectors, axis=0)
        return vector

    def rerank(self, retrieve_result_list, id_pair_list):
        re = []
        for index, retrieve_result in enumerate(retrieve_result_list):
            score = (self.wb * retrieve_result["beh"] + self.wp * retrieve_result["ps_pt"] + self.wr * retrieve_result["rs_rt"]) / 3
            re.append({"score": score, "method_1": id_pair_list[index][0], "method_2": id_pair_list[index][1], "extra": retrieve_result})

        re = sorted(re, key=lambda k: k['score'], reverse=True)
        return re

    def calculate_vector_distance(self, vector1, vector2):
        vector1 = np.array(vector1)
        vector2 = np.array(vector2)
        cos = vector1.dot(vector2) / (np.linalg.norm(vector1) * np.linalg.norm(vector2))

        return cos


if __name__ == '__main__':
    pass