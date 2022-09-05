# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-----------------------------------------
@Author: zz
@Email: 21212010059@m.fudan.edu.cn
@Created: 2022/07/22
------------------------------------------
@Modify: 2022/07/22
------------------------------------------
@Description:
"""
import os
import threading
import time
from definitions import DATA_DIR, OUTPUT_DIR
from migration.calculator.base import MultiCombineSimResultCollection
from migration.calculator.constant import Constant
from migration.calculator.factory import MilvusSimFactory
from migration.evaluate.base import SimEvaluator
from migration.evaluate.dataset import DataSet
from migration.pipeline import APIMigration
from migration.util.db_util import DBUtil
from migration.util.file_util import FileUtil
from migration.util.milvus_util import MilvusUtil
from migration.util.neo4j_util import Neo4jUtil
from migration.util.path_util import PathUtil

# test/big + /transE/rank + /icpc_saner/segicpc +  /single  +retrieve/rarank + method/class + /filter + model/evaluate/export_result
vector_type = "_without_functionality"
big_or_small = "small"
type = "test"
filter = "_filter"


def create_method_pipeline(milvus, neo4j_util, library2methods, milvus_util):
    factory = MilvusSimFactory(milvus=milvus, neo4j_util=neo4j_util, collection_name="migration_{}_test{}".format(big_or_small, vector_type), partition_name=Constant.METHOD, relation_embedding_path=PathUtil.complex_relation_file("relation_types_parameters_apikg_test_821{}.tsv".format(vector_type)))
    migration = APIMigration(neo4j_util, library2methods, milvus_util, big_or_small, vector_type)
    migration.add_calculator(calculator=factory.method2method_milvus_sim(), name="method->method")
    return migration

def gene_temp_data(index, start, end):
    csv_path = os.path.join(DATA_DIR, 'query_data', 'APIMigrationBenchmark_method_{}.csv'.format(type))
    dataset = DataSet("method")
    dataset.load_from_csv(csv_path)
    top_n = 3000
    library2methods = FileUtil.load_data_list(os.path.join(DATA_DIR, "icpc_saner", "all_library_method_dic_{}.json".format(type)))
    if type == "test":
        migration = create_method_pipeline(milvus=DBUtil.get_milvus(), neo4j_util=DBUtil.get_test_api_kg_util(), library2methods=library2methods, milvus_util=DBUtil.get_milvus_util())
    else:
        migration = create_method_pipeline(milvus=DBUtil.get_milvus(), neo4j_util=DBUtil.get_large_api_kg_util(), library2methods=library2methods, milvus_util=DBUtil.get_milvus_util())
    print(migration)

    final_retrieval_sim_collection = MultiCombineSimResultCollection()
    count = 0
    for ind, query_pair in enumerate(dataset.query_data):
        if ind < start or ind > end:
            continue

        temp_query_pair = [
            {"query_id": int(query_pair[dataset.position_a]), "target_id": int(query_pair[dataset.position_b])},
            {"query_id": int(query_pair[dataset.position_b]), "target_id": int(query_pair[dataset.position_a])}]
        for t in temp_query_pair:
            try:
                count = count + 1
                print("thread", index, "complete ", count, str(t["query_id"]) + "_" + str(t["target_id"]))
                if filter == "":
                    rerank_combine_sim_collection, retrieval_combine_sim_collection, complete_retrieval_combine_sim_collection = migration.run(
                        start_api_id=t["query_id"], retrieval_top_n=top_n, is_filter=True, rerank_top_n=top_n,
                        return_retrieval_result=True, is_complete=False)
                else:
                    rerank_combine_sim_collection, retrieval_combine_sim_collection, complete_retrieval_combine_sim_collection = migration.run(
                        start_api_id=t["query_id"], retrieval_top_n=top_n, is_filter=True, rerank_top_n=top_n,
                        return_retrieval_result=True, is_complete=False, target_api_id=t["target_id"])
            except BaseException as e:
                print("thread", index, "error ", count, str(t["query_id"]) + "_" + str(t["target_id"]), e)
                retrieval_combine_sim_collection = None
            final_retrieval_sim_collection.add(str(t["query_id"]) + "_" + str(t["target_id"]), retrieval_combine_sim_collection)

    final_retrieval_sim_collection.save(PathUtil.temp_multi_combine_sim_collection("{}{}_single_retrieve_method{}_model_{}".format(type, vector_type, filter, str(index))))
    print("save {}{}_single_retrieve_method{}_model_{} success".format(type, vector_type, filter, str(index)))


def merge(thread_num):
    retrieve_result = None
    for index in range(thread_num):
        if retrieve_result is None:
            retrieve_result: MultiCombineSimResultCollection = MultiCombineSimResultCollection.load(PathUtil.temp_multi_combine_sim_collection("{}{}_single_retrieve_method{}_model_{}".format(type, vector_type, filter, str(index+1))))
        else:
            retrieve: MultiCombineSimResultCollection = MultiCombineSimResultCollection.load(PathUtil.temp_multi_combine_sim_collection("{}{}_single_retrieve_method{}_model_{}".format(type, vector_type, filter, str(index+1))))
            id2csrc = retrieve.id2name2sim_collection
            retrieve_result.id2name2sim_collection.update(id2csrc)

    retrieve_result.save(PathUtil.multi_combine_sim_collection("{}{}_single_retrieve_method{}_model").format(type, vector_type, filter))
    print("save {}{}_single_retrieve_method{}_model success".format(type, vector_type, filter))


if __name__ == '__main__':
    time1 = time.time()
    # 加载数据
    csv_path = os.path.join(DATA_DIR, 'query_data', 'APIMigrationBenchmark_method_{}.csv'.format(type))
    dataset = DataSet("method")
    dataset.load_from_csv(csv_path)
    length = len(dataset.query_data)
    batch_size = 500
    batch_num = length // batch_size
    if length % batch_size != 0:
        batch_num = batch_num + 1
    threads = []
    for index in range(batch_num):
        start = index * batch_size
        end = (index + 1) * batch_size

        threads.append(threading.Thread(
            target=gene_temp_data,
            args=(index + 1, start, end)
        ))
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    merge(batch_num)
    time2 = time.time()
    '''
    ==============================================================================================================
    ==============================================================================================================
    '''
    # 加载数据
    csv_path = os.path.join(DATA_DIR, 'query_data', 'APIMigrationBenchmark_method_{}.csv'.format(type))
    dataset = DataSet("method")
    dataset.load_from_csv(csv_path)
    # 加载评估器
    filter_top_n = 3000
    top_n = 200
    top_n_list = [1, 3, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 3000]
    se = SimEvaluator(top_n)
    eval_data_list = []
    retrieve: MultiCombineSimResultCollection = MultiCombineSimResultCollection.load(PathUtil.multi_combine_sim_collection("{}{}_single_retrieve_method{}_model".format(type, vector_type, filter)))
    retrieve_id2name2sim_collection = retrieve.id2name2sim_collection

    eval_result_list = []
    count = 0
    name2weight = {
        "method->method": 1
    }

    try:
        se.evaluate(dataset=dataset, top_n_list=top_n_list, multi_combine_sim_result_collection=retrieve, combine_sim_result_collection_type="retrieve", msimcol_name="{}{}_single_retrieve_method{}_model".format(type, vector_type, filter), name2weight=name2weight)
        count = count + 1
        print("evaluate: ", count)
        print(se.eval_result)
        eval_result_list.append(se.eval_result)
    except BaseException as e:
        print(e)

    FileUtil.write2json(os.path.join(OUTPUT_DIR, "evaluate", "{}{}_single_method{}_evaluate.json".format(type, vector_type, filter)), eval_result_list)
    print("write {}{}_single_method{}_evaluate success".format(type, vector_type, filter))
    time3 = time.time()

    '''
    ==============================================================================================================
    ==============================================================================================================
    '''
    # start_time = time.time()
    # top_n = 50
    # se = SimEvaluator(top_n)
    # csv_path = os.path.join(DATA_DIR, 'query_data', 'APIMigrationBenchmark_method_{}.csv'.format(type))
    # dataset = DataSet("method")
    # dataset.load_from_csv(csv_path)
    # milvus = DBUtil.get_milvus()
    # library2methods = FileUtil.load_data_list(os.path.join(DATA_DIR, "icpc_saner", "all_library_method_dic_{}.json".format(type)))
    # if type == "test":
    #     graph_util = DBUtil.get_test_api_kg_util()
    #     migration = create_method_pipeline(milvus=DBUtil.get_milvus(), neo4j_util=DBUtil.get_test_api_kg_util(), library2methods=library2methods, milvus_util=DBUtil.get_milvus_util())
    #
    # else:
    #     graph_util = DBUtil.get_large_api_kg_util()
    #     migration = create_method_pipeline(milvus=DBUtil.get_milvus(), neo4j_util=DBUtil.get_large_api_kg_util(), library2methods=library2methods, milvus_util=DBUtil.get_milvus_util())
    #
    # milvus_util = MilvusUtil(DBUtil.get_milvus())
    # retrieval_combine_sim_collection: MultiCombineSimResultCollection = MultiCombineSimResultCollection.load(PathUtil.multi_combine_sim_collection("{}{}_single_retrieve_method{}_model".format(type, vector_type, filter)))
    #
    # name2model = {
    #     "{}{}_single_retrieve_method{}_model".format(type, vector_type, filter): retrieval_combine_sim_collection
    # }
    #
    # data_list = FileUtil.load_data_list(os.path.join(OUTPUT_DIR, "evaluate", "{}{}_single_method{}_evaluate.json".format(type, vector_type, filter)))
    #
    # for index, data in enumerate(data_list):
    #     result_list = []
    #     count = 0
    #     for query_pair in dataset.query_data:
    #         temp_query_pair = [
    #             {"query_id": int(query_pair[dataset.position_a]), "target_id": int(query_pair[dataset.position_b])},
    #             {"query_id": int(query_pair[dataset.position_b]), "target_id": int(query_pair[dataset.position_a])}]
    #
    #         for t in temp_query_pair:
    #             result = {}
    #             result["start_node_info"] = graph_util.get_node_by_id(t["query_id"])
    #             result["start_node_neighbour_info"] = graph_util.get_neighbour_by_id(t["query_id"])
    #             result["target_node_info"] = graph_util.get_node_by_id(t["target_id"])
    #             result["target_node_neighbour_info"] = graph_util.get_neighbour_by_id(t["target_id"])
    #             result["top_n"] = top_n
    #             result["distance"] = milvus_util.calculate_distance_by_id(t["query_id"], t["target_id"], collection_name="migration_{}_test{}".format(big_or_small, vector_type))
    #             result["position"] = -1
    #             try:
    #                 result["filter_retention_info"] = \
    #                 name2model[data["details"][0]["msimcol_name"]].id2name2sim_collection[
    #                     str(t["query_id"]) + "_" + str(t["target_id"])].name2filter_retention_num
    #             except BaseException as e:
    #                 result["filter_retention_info"] = {}
    #                 print(e, t)
    #             try:
    #                 combine_results = name2model[data["details"][0]["msimcol_name"]].id2name2sim_collection[
    #                     str(t["query_id"]) + "_" + str(t["target_id"])].get_combine_sim_result(
    #                     data["details"][0]["name2weight"])
    #                 result["combine_results"] = []
    #                 for inde, te in enumerate(combine_results[:result["top_n"]]):
    #                     combine_result = {
    #                         "node_info": graph_util.get_node_by_id(te.end_id),
    #                         "node_neighbour_info": graph_util.get_neighbour_by_id(te.end_id),
    #                         "score": te.score,
    #                         "extra": te.extra
    #                     }
    #                     result["combine_results"].append(combine_result)
    #                     if te.end_id == t["target_id"]:
    #                         result["position"] = inde
    #                 count = count + 1
    #                 print("process: ", index, count)
    #                 result_list.append(result)
    #             except BaseException as e:
    #                 print(e, t)
    #
    #     FileUtil.write2json(os.path.join(OUTPUT_DIR, "export_result", "{}{}_single_method{}_export_result_{}.json".format(type, vector_type, filter, index + 1)), result_list)
    #     print("write ", "{}{}_single_method{}_export_result_{}.json".format(type, vector_type, filter, index + 1), "success")
    # time4 = time.time()
    # print(time1)
    # print(time2)
    # print(time3)
    # print(time4)
    #






