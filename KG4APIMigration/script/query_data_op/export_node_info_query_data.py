# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-----------------------------------------
@Author: zz
@Email: 21212010059@m.fudan.edu.cn
@Created: 2022/07/27
------------------------------------------
@Modify: 2022/07/27
------------------------------------------
@Description:
"""
import os
from migration.util.db_util import DBUtil
from definitions import DATA_DIR, OUTPUT_DIR
from migration.util.file_util import FileUtil

graph_util = DBUtil.get_test_api_kg_util()

position_a = 3
position_b = 7
path = os.path.join(DATA_DIR, "query_data", "APIMigrationBenchmark_method.csv")
result = []
ids = []
with open(path) as f:
    lines = f.readlines()
    lines = [line.strip().split(',') for line in lines]
    for line in lines:
        if int(line[position_a]) not in ids:
            ids.append(int(line[position_a]))
        if int(line[position_b]) not in ids:
            ids.append(int(line[position_b]))

for index, id in enumerate(ids):
    print("process", index, id)
    out_re = graph_util.get_two_step_neighbour_by_id(id)
    result.append(out_re)

FileUtil.write2json(os.path.join(OUTPUT_DIR, "export_result", "node_info_method.json"), result)
'''
====================================================================================================================
'''
# position_a = 2
# position_b = 6
# path = os.path.join(DATA_DIR, "query_data", "APIMigrationBenchmark_class.csv")
# result = []
# ids = []
# with open(path) as f:
#     lines = f.readlines()
#     lines = [line.strip().split(',') for line in lines]
#     for line in lines:
#         if int(line[position_a]) not in ids:
#             ids.append(int(line[position_a]))
#         if int(line[position_b]) not in ids:
#             ids.append(int(line[position_b]))
#
# for index, id in enumerate(ids):
#     print("process", index, id)
#     out_re = graph_util.get_two_step_neighbour_by_id(id)
#     result.append(out_re)
#
# FileUtil.write2json(os.path.join(OUTPUT_DIR, "export_result", "node_info_class.json"), result)




