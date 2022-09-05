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
import os
from queue import Queue
from py2neo import Graph
from definitions import DATA_DIR, TestNEO4J, LargeNEO4J
from migration.rapim.neo4j_op import QueryData
from migration.util.db_util import DBUtil
from migration.util.file_util import FileUtil

type = "test"


position_a = 3
position_b = 7
file = os.path.join(DATA_DIR, "query_data", "APIMigrationBenchmark_method_{}.csv".format(type))

all_method_ids = []
all_library_ids = []
all_library_method_dic = {}
with open(file) as f:
    lines = f.readlines()
    lines = [line.strip().split(',') for line in lines]
    clean_lines = []
    for line in lines:
        if line[position_a] != '-1' and line[position_b] != '-1' and line[position_a] != -1 and line[position_b] != -1:
            if line[position_a] not in all_method_ids:
                all_method_ids.append(line[position_a])
            if line[position_b] not in all_method_ids:
                all_method_ids.append(line[position_b])

if type == "big":
    graph_util = DBUtil.get_large_api_kg_util()
    graph = DBUtil.get_large_api_kg()
else:
    graph_util = DBUtil.get_test_api_kg_util()
    graph = DBUtil.get_test_api_kg()

print(len(all_method_ids))
for id in all_method_ids:
    l_id = graph_util.get_library_id_by_node_id(id)
    if l_id != -1:
        if l_id not in all_library_ids:
            all_library_ids.append(l_id)

print(len(all_library_ids))


for l_id in all_library_ids:

    cypher = "MATCH (l:library)-[:include]->(p:packages)<-[:exists_in]-(c)<-[:belong_to]-(m:method)  where l.library_id={} return id(m)  ".format(l_id)

    data_list = graph.run(cypher).data()

    temp = []
    for data in data_list:
        data = dict(data)
        temp.append(int(data["id(m)"]))
    all_library_method_dic[str(l_id)] = temp

FileUtil.write2json(os.path.join(DATA_DIR, "icpc_saner", "all_library_method_dic_{}.json".format(type)), all_library_method_dic)


'''
============================================================================================================================================
'''

# if type == "test":
#     graph = DBUtil.get_test_api_kg()
# else:
#     graph = DBUtil.get_large_api_kg()
#
#
# result = {}
# count = 0
# err_count = 0
# file = os.path.join(DATA_DIR, "icpc_saner", "all_library_method_dic_{}.json".format(type))
# library2methods = FileUtil.load_data_list(file)
# for k, v in library2methods.items():
#     for node_id in v:
#         if result.get(str(node_id), {}) == {}:
#
#             try:
#                 re = {
#                     "method_name": "",
#                     "method_description": "",
#                     "parameter_signature": "",
#                     "parameter_description": "",
#                     "parameters": [],
#                     "package_name": "",
#                     "return_value_description": "",
#                     "return_value_type_id": -1,
#                     "return_value_type_name": ""
#                 }
#
#                 cypher = "match (rt)<-[:return_value_type_of]-(r:return_value)<-[:has_return_value]-(m:method)-[:belong_to]->(c)-[:exists_in]->" \
#                          "(p:packages) where id(m)={} return rt, r, m, p, id(rt)".format(node_id)
#                 data_list = graph.run(cypher).data()
#                 for data in data_list:
#                     rt = dict(data["rt"])
#                     r = dict(data["r"])
#                     m = dict(data["m"])
#                     p = dict(data["p"])
#
#                     method_description = m.get("description", "")
#                     method_name = m.get("name", "")
#                     parameter_signature = method_name[method_name.find("("):].replace("(", "").replace(")", "")
#                     method_name = method_name[:method_name.find("(")]
#                     package_name = p.get("qualified_name", "")
#                     return_value_description = r.get("description", "")
#                     return_value_type_name = rt.get("name", "")
#                     return_value_type_id = data["id(rt)"]
#
#                     re["method_name"] = method_name
#                     re["method_description"] = method_description
#                     re["package_name"] = package_name
#                     re["return_value_description"] = return_value_description
#                     re["return_value_type_name"] = return_value_type_name
#                     re["return_value_type_id"] = return_value_type_id
#                     re["parameter_signature"] = parameter_signature
#
#                 cypher = "match(m:method)-[:has_parameter]-(p) where id(m)={} return p".format(node_id)
#                 data_list = graph.run(cypher).data()
#                 parameter_description_list = []
#                 for data in data_list:
#                     p = dict(data["p"])
#                     parameter_description = p.get("description", "")
#                     parameter_name = p.get("name", "")
#                     parameter_type = p.get("type", "")
#                     if parameter_description != "":
#                         parameter_description_list.append(parameter_description)
#                     if parameter_name != "" and parameter_type != "":
#                         re["parameters"].append({"parameter_name": parameter_name, "parameter_type": parameter_type})
#
#                 re["parameter_description"] = " ".join(parameter_description_list)
#                 result[str(node_id)] = re
#                 count = count + 1
#                 print("process ", count, node_id)
#             except BaseException as e:
#                 err_count = err_count + 1
#                 print("error", err_count, node_id, e)
#
# filename = os.path.join(DATA_DIR, "icpc_saner", "all_library_method_info_dic_{}.json".format(type))
# FileUtil.write2json(filename, result)
# print("write ", filename, "success")


