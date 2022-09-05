# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-----------------------------------------
@Author: zz
@Email: 21212010059@m.fudan.edu.cn
@Created: 2022/07/15
------------------------------------------
@Modify: 2022/07/15
------------------------------------------
@Description:
"""
import os
import time
import numpy as np
from migration.calculator.base import MultiCombineSimResultCollection, CombineSimResultCollection
from migration.calculator.constant import Constant
from migration.calculator.factory import MilvusSimFactory
from migration.evaluate.base import SimEvaluator
from migration.evaluate.dataset import DataSet
from migration.pipeline import APIMigration
from migration.util.db_util import DBUtil
from migration.util.file_util import FileUtil
from migration.util.neo4j_util import Neo4jUtil
from migration.util.path_util import PathUtil
from definitions import DATA_DIR, OUTPUT_DIR

vector_type = "_complex_logistic_300_all"

type = "test"
big_or_small = "small"
filter = ""


def find_optimal_result(file, beam_size=4):

    dl = FileUtil.load_data_list_from_json(file)
    dl = sorted(dl, key=lambda x: x["rank"], reverse=False)
    dl = sorted(dl, key=lambda x: x["mrr"], reverse=True)
    dl = dl[:beam_size]
    nl = []
    for data in dl:
        nl.append(data["details"][0]["name2weight"])
    return nl, dl


if __name__ == '__main__':
    time1 = time.time()
    beam_size = 4
    # 加载评估器和数据
    top_n = 100
    top_n_list = [1, 3, 5, 10, 20, 30, 50, 100]
    se = SimEvaluator(top_n)
    csv_path = os.path.join(DATA_DIR, 'query_data', 'APIMigrationBenchmark_method_{}_shuffle.csv'.format(type))
    dataset = DataSet(data_type="method")
    dataset.load_from_csv(csv_path)

    all_train_data = []
    for i in range(10):
        all_train_data.append(dataset.split(i+1)[0])
    # 加载已经储存的数据
    rerank: MultiCombineSimResultCollection = MultiCombineSimResultCollection.load(PathUtil.multi_combine_sim_collection("{}_rerank_method{}_model".format(type, filter)))
    rerank_id2name2sim_collection = rerank.id2name2sim_collection
    step = 0.05
    steps = list(np.around(np.arange(0, 1.01, step), decimals=2))
    steps.reverse()
    parameter_to_be_change_list = [
        "class concepts of method->class concepts of method",
        # "neighbor concepts of method->neighbor concepts of method",
        "functionalities of method->functionalities of method",
        "return value type concepts of method->return value type concepts of method",
        "parameter type concepts of method->parameter type concepts of method",
        "parameter concepts of method->parameter concepts of method",
        "method->method"
    ]
    for index, train_data in enumerate(all_train_data):
        count = 0
        for parameter_to_be_change in parameter_to_be_change_list:
            if parameter_to_be_change == "class concepts of method->class concepts of method":
                name2weight_list = [{
                           "class concepts of method->class concepts of method": 0,
                           "neighbor concepts of method->neighbor concepts of method": 0,
                           "functionalities of method->functionalities of method": 0,
                           "return value type concepts of method->return value type concepts of method": 0,
                           "parameter type concepts of method->parameter type concepts of method": 0,
                           "parameter concepts of method->parameter concepts of method": 0,
                           "method->method": 1.0,
                }]
                test_result_list = []
                eval_result_list = []
                for name2weight in name2weight_list:
                    for i1 in steps:
                        name2weight[parameter_to_be_change] = i1
                        try:
                            se.evaluate(dataset=train_data, top_n_list=top_n_list,
                                        multi_combine_sim_result_collection=rerank,
                                        combine_sim_result_collection_type="rerank",
                                        msimcol_name="{}_rerank_method{}_model".format(type, filter),
                                        name2weight=name2weight)
                            count = count + 1
                            print("epoch: ", index, "count: ", count, len(train_data.query_data))
                            eval_result_list.append(se.eval_result.copy())
                        except BaseException as e:
                            print(e)
                            print(name2weight)

                FileUtil.write2json(os.path.join(OUTPUT_DIR, "evaluate", "{}_method_evaluate_all_split_beam_search_{}.json".format(type, index)), eval_result_list)
                name2weight_list, data_list = find_optimal_result(os.path.join(OUTPUT_DIR, "evaluate", "{}_method_evaluate_all_split_beam_search_{}.json".format(type, index)), beam_size)
                FileUtil.write2json(os.path.join(OUTPUT_DIR, "evaluate", "final_{}_method_evaluate_all_split_{}_{}_without_neighbour.json".format(type, parameter_to_be_change.replace(" ", "_").replace("->", "_"), index)), data_list)


            else:
                name2weight_list, data_list = find_optimal_result(os.path.join(OUTPUT_DIR, "evaluate", "{}_method_evaluate_all_split_beam_search_{}.json".format(type, index)), beam_size)
                eval_result_list = []
                for name2weight in name2weight_list:
                    for i1 in steps:
                        name2weight[parameter_to_be_change] = i1
                        try:
                            se.evaluate(dataset=train_data, top_n_list=top_n_list,
                                        multi_combine_sim_result_collection=rerank,
                                        combine_sim_result_collection_type="rerank",
                                        msimcol_name="{}_rerank_method{}_model".format(type, filter),
                                        name2weight=name2weight)
                            count = count + 1
                            print("epoch: ", index, "count: ", count, len(train_data.query_data))
                            eval_result_list.append(se.eval_result.copy())
                        except BaseException as e:
                            print(e)
                            print(name2weight)

                FileUtil.write2json(os.path.join(OUTPUT_DIR, "evaluate", "{}_method_evaluate_all_split_beam_search_{}.json".format(type, index)), eval_result_list)
                name2weight_list, data_list = find_optimal_result(os.path.join(OUTPUT_DIR, "evaluate", "{}_method_evaluate_all_split_beam_search_{}.json".format(type, index)), beam_size)
                FileUtil.write2json(os.path.join(OUTPUT_DIR, "evaluate", "final_{}_method_evaluate_all_split_{}_{}_without_neighbour.json".format(type, parameter_to_be_change.replace(" ", "_").replace("->", "_"), index)),  data_list)



