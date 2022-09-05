# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-----------------------------------------
@Author: zz
@Email: 21212010059@m.fudan.edu.cn
@Created: 2022/08/28
------------------------------------------
@Modify: 2022/08/28
------------------------------------------
@Description:
"""
import os

from definitions import DATA_DIR, OUTPUT_DIR
from migration.calculator.base import MultiCombineSimResultCollection
from migration.converter.filter import NodeFilter
from migration.evaluate.base import SimEvaluator
from migration.evaluate.dataset import DataSet
from migration.util.db_util import DBUtil
from migration.util.file_util import FileUtil
from migration.util.path_util import PathUtil

if __name__ == '__main__':
    vector_type = ""
    type = "big"
    big_or_small = "big"
    filter = "_filter"

    csv_path = os.path.join(DATA_DIR, 'query_data', 'APIMigrationBenchmark_method_{}.csv'.format(type))
    dataset = DataSet("method")
    dataset.load_from_csv(csv_path)
    # 加载评估器
    filter_top_n = 10
    top_n = 10
    top_n_list = [1, 3, 5, 10]
    se = SimEvaluator(top_n)
    # 加载migration pipeline
    milvus = DBUtil.get_milvus()

    if type == "big":
        graph_util = DBUtil.get_large_api_kg_util()
    else:
        graph_util = DBUtil.get_test_api_kg_util()

    # node_filter = NodeFilter(graph_util)
    node_filter = None
    filter_library = True
    filter_class = False

    rerank: MultiCombineSimResultCollection = MultiCombineSimResultCollection.load(
        PathUtil.multi_combine_sim_collection("{}_rerank_method{}_model".format(type, filter)))
    rerank_id2name2sim_collection = rerank.id2name2sim_collection

    eval_result_list = []
    count = 0

    name2weight = {
        "method->method": 0.05,
        "parameter type concepts of method->parameter type concepts of method": 0.25,
        "parameter concepts of method->parameter concepts of method": 0.05,
        "class concepts of method->class concepts of method": 0.8,
        "functionalities of method->functionalities of method": 0.95,
        "neighbor concepts of method->neighbor concepts of method": 0.95,
        "return value type concepts of method->return value type concepts of method": 0.05
    }

    # name2weight = {
    #     "method->method": 1,
    #     "parameter type concepts of method->parameter type concepts of method": 0,
    #     "parameter concepts of method->parameter concepts of method": 0,
    #     "class concepts of method->class concepts of method": 0,
    #     "functionalities of method->functionalities of method": 0,
    #     "neighbor concepts of method->neighbor concepts of method": 0,
    #     "return value type concepts of method->return value type concepts of method": 0
    # }

    # name2weight = {"model": 1}

    try:
        se.evaluate(dataset=dataset, top_n_list=top_n_list, multi_combine_sim_result_collection=rerank,
                    combine_sim_result_collection_type="rerank",
                    msimcol_name="{}_rerank_method{}_model".format(type, filter), name2weight=name2weight,
                    node_filter=node_filter, filter_in_library=filter_library)
        count = count + 1
        print("evaluate: ", count)
        eval_result_list.append(se.eval_result)
    except BaseException as e:
        print(e)
    FileUtil.write2json(os.path.join(OUTPUT_DIR, "evaluate", "{}_apimigration_rerank{}.json".format(type, filter)), eval_result_list)

