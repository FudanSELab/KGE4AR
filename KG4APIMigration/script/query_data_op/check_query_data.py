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
from definitions import DATA_DIR, OUTPUT_DIR
from migration.util.file_util import FileUtil


def check_query_data_pipeline(file_pair_list, type):
    method_set = []
    library_map = {}
    result_data_list = []

    for file_pair in file_pair_list:
        now_method_set = []
        now_library_map = {}

        with open(file_pair[0]) as f:
            linesA = f.readlines()
            linesA = [lineA.strip() for lineA in linesA]
        with open(file_pair[1]) as f:
            linesB = f.readlines()
            linesB = [lineB.strip() for lineB in linesB]
        with open(file_pair[2]) as f:
            linesAB = f.readlines()
            linesAB = [lineAB.strip().split(',') for lineAB in linesAB]
        for index, line in enumerate(linesA):
            lineA = linesA[index]
            lineB = linesB[index]
            lineAB = linesAB[index]
            if lineAB[3] == -1 or lineAB[3] == "-1":
                method = lineA
                if "<L>no" in method or "<L>many" in method:
                    continue
                if method not in now_method_set:
                    now_method_set.append(method)
                    library = method.split("<L>")[0]
                    now_library_map[library] = now_library_map.get(library, 0) + 1
                if method not in method_set:
                    method_set.append(method)
                    library = method.split("<L>")[0]
                    library_map[library] = library_map.get(library, 0) + 1

            if lineAB[7] == -1 or lineAB[7] == "-1":
                method = lineB
                if "<L>no" in method or "<L>many" in method:
                    continue
                if method not in now_method_set:
                    now_method_set.append(method)
                    library = method.split("<L>")[0]
                    now_library_map[library] = now_library_map.get(library, 0) + 1
                if method not in method_set:
                    method_set.append(method)
                    library = method.split("<L>")[0]
                    library_map[library] = library_map.get(library, 0) + 1


        result_data = {"file_name": file_pair[2], "now_hit_method_num": len(now_method_set), "no_hit_method": now_method_set, "no_hit_library": now_library_map}
        result_data_list.append(result_data)

    result_data = {"file_name": "merge_file", "now_hit_method_num": len(method_set), "no_hit_method": method_set, "no_hit_library": library_map}
    result_data_list.append(result_data)
    FileUtil.write2json(os.path.join(OUTPUT_DIR, "export_result", "check_query_data_{}.json".format(type)), result_data_list)

if __name__ == '__main__':
    type = "test"


    file_pair_list = [
        [os.path.join(DATA_DIR, "query_data", "ICPC19MethodMigrationA.txt"),
         os.path.join(DATA_DIR, "query_data", "ICPC19MethodMigrationB.txt"),
         os.path.join(DATA_DIR, "query_data", "ICPC19MethodMigration_{}.csv".format(type))],
        [os.path.join(DATA_DIR, "query_data", "TSE19MethodMigrationA.txt"),
         os.path.join(DATA_DIR, "query_data", "TSE19MethodMigrationB.txt"),
         os.path.join(DATA_DIR, "query_data", "TSE19MethodMigration_{}.csv".format(type))]
    ]
    check_query_data_pipeline(file_pair_list, type)