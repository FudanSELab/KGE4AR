# !/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from definitions import DATA_DIR


def count_query_data_pipeline(file_pair_list):
    all_pair_num = 0
    mark_pair_num = 0
    hit_pair_num = 0
    distinct_hit_pair_num = 0
    pair_set = set([])

    for file_pair in file_pair_list:
        now_all_pair_num = 0
        now_mark_pair_num = 0
        now_hit_pair_num = 0
        now_distinct_hit_pair_num = 0
        now_pair_set = set([])

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
            now_all_pair_num = now_all_pair_num + 1
            all_pair_num = all_pair_num + 1

            if lineA[len(lineA)-5:] != "<L>no" and lineA[len(lineA)-7:] != "<L>many" and lineB[len(lineB)-5:] != "<L>no" and lineB[len(lineB)-7:] != "<L>many":
                now_mark_pair_num = now_mark_pair_num + 1
                mark_pair_num = mark_pair_num + 1
                if lineAB[3] != -1 and lineAB[3] != "-1" and lineAB[7] != -1 and lineAB[7] != "-1":
                    now_hit_pair_num = now_hit_pair_num + 1
                    hit_pair_num = hit_pair_num + 1
                    if str(lineAB[3]) + '-' + str(lineAB[7]) not in now_pair_set:
                        now_pair_set.add(str(lineAB[3]) + '-' + str(lineAB[7]))
                        now_pair_set.add(str(lineAB[7]) + '-' + str(lineAB[3]))
                        now_distinct_hit_pair_num = now_distinct_hit_pair_num + 1
                    if str(lineAB[3]) + '-' + str(lineAB[7]) not in pair_set:
                        pair_set.add(str(lineAB[3]) + '-' + str(lineAB[7]))
                        pair_set.add(str(lineAB[7]) + '-' + str(lineAB[3]))
                        distinct_hit_pair_num = distinct_hit_pair_num + 1

        print(file_pair[2], "all_pair_num: ", now_all_pair_num)
        print(file_pair[2], "mark_pair_num: ", now_mark_pair_num)
        print(file_pair[2], "hit_pair_num: ", now_hit_pair_num)
        print(file_pair[2], "distinct_hit_pair_num: ", now_distinct_hit_pair_num)


    print("merge file, all_pair_num: ", all_pair_num)
    print("merge file, mark_pair_num: ", mark_pair_num)
    print("merge file, hit_pair_num: ", hit_pair_num)
    print("merge file, distinct_hit_pair_num: ", distinct_hit_pair_num)


if __name__ == '__main__':
    file_pair_list = [
        [os.path.join(DATA_DIR, "query_data", "ICPC19MethodMigrationA.txt"),
         os.path.join(DATA_DIR, "query_data", "ICPC19MethodMigrationB.txt"),
         os.path.join(DATA_DIR, "query_data", "ICPC19MethodMigration.csv")],
        [os.path.join(DATA_DIR, "query_data", "TSE19MethodMigrationA.txt"),
         os.path.join(DATA_DIR, "query_data", "TSE19MethodMigrationB.txt"),
         os.path.join(DATA_DIR, "query_data", "TSE19MethodMigration.csv")]
    ]
    count_query_data_pipeline(file_pair_list)