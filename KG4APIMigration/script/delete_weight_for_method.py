# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-----------------------------------------
@Author: zz
@Email: 21212010059@m.fudan.edu.cn
@Created: 2022/08/30
------------------------------------------
@Modify: 2022/08/30
------------------------------------------
@Description:
"""
import os
import time

from definitions import DATA_DIR
from migration.calculator.base import MultiCombineSimResultCollection
from migration.evaluate.base import SimEvaluator
from migration.evaluate.dataset import DataSet
from migration.util.file_util import FileUtil
from migration.util.path_util import PathUtil

vector_type = "v2"

type = "big"
big_or_small = "big"
filter = "_filter"


if __name__ == '__main__':
    time1 = time.time()
    # 加载评估器和数据
    top_n = 100
    top_n_list = [1, 3, 5, 10, 20, 30, 50, 100]
    se = SimEvaluator(top_n)
    csv_path = os.path.join(DATA_DIR, 'query_data', 'APIMigrationBenchmark_method_{}.csv'.format(type))
    dataset = DataSet(data_type="method")
    dataset.load_from_csv(csv_path)

    # 加载已经储存的数据
    rerank: MultiCombineSimResultCollection = MultiCombineSimResultCollection.load(PathUtil.multi_combine_sim_collection("{}_2_rerank_method{}_model".format(type, filter)))
    rerank_id2name2sim_collection = rerank.id2name2sim_collection
    eval_result_list = []
    name2weight = {
        "method->method": 0.4,
                    "parameter type concepts of method->parameter type concepts of method": 0.2,
                    "parameter concepts of method->parameter concepts of method": 0.05,
                    "class concepts of method->class concepts of method": 0.8,
                    "functionalities of method->functionalities of method": 0.9,
                    "neighbor concepts of method->neighbor concepts of method": 0,
                    "return value type concepts of method->return value type concepts of method": 0.05
    }

    try:
        se.evaluate(dataset=dataset, top_n_list=top_n_list, multi_combine_sim_result_collection=rerank,
                    combine_sim_result_collection_type="rerank",
                    msimcol_name="{}_2_rerank_method{}_model".format(type, filter), name2weight=name2weight)

        print("name:  all", )
        eval_result_list.append(se.eval_result)
    except BaseException as e:
        print(e)

    for name, weight in name2weight.items():
        memory = name2weight[name]
        name2weight[name] = 0
        try:
            se.evaluate(dataset=dataset, top_n_list=top_n_list, multi_combine_sim_result_collection=rerank,
                        combine_sim_result_collection_type="rerank",
                        msimcol_name="{}_2_rerank_method{}_model".format(type, filter), name2weight=name2weight)

            print("name: ", name)
            eval_result_list.append(se.eval_result)
        except BaseException as e:
            print(e)
        name2weight[name] = memory

    FileUtil.write2json("delete2_without_neighbour.json", eval_result_list)






