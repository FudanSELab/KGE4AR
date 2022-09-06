# !/usr/bin/env python
# -*- coding: utf-8 -*-
import cProfile
import os
import threading
import time
from definitions import DATA_DIR, OUTPUT_DIR
from migration.calculator.base import MultiCombineSimResultCollection, CombineSimResultCollection
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

# test/big + /transE/rank + /icpc_saner/segicpc +  /single  +retrieve/rarank  + method/class + /filter + model/evaluate/export_result

vector_type = "_v2"

type = "big"
big_or_small = "big"
filter = "_filter"

def create_method_pipeline(milvus, neo4j_util, library2methods, milvus_util):
    factory = MilvusSimFactory(milvus=milvus, neo4j_util=neo4j_util, collection_name="migration_{}_test{}".format(big_or_small, vector_type), partition_name=Constant.METHOD)

    migration = APIMigration(neo4j_util, library2methods, milvus_util, big_or_small, vector_type)
    migration.add_calculator(calculator=factory.method2method_milvus_sim(),
                             name="method->method")
    # 添加rerank模块
    migration.add_calculator(calculator=factory.class_concepts_of_method2class_concepts_of_method_milvus_sim(),
                             name="class concepts of method->class concepts of method",
                             stage=APIMigration.STAGE_RERANK)
    migration.add_calculator(calculator=factory.parameter_concepts_of_method2parameter_concepts_of_method_milvus_sim(),
                             name="parameter concepts of method->parameter concepts of method",
                             stage=APIMigration.STAGE_RERANK)
    migration.add_calculator(calculator=factory.parameter_type_concepts_of_method2parameter_type_concepts_of_method_milvus_sim(),
                             name="parameter type concepts of method->parameter type concepts of method",
                             stage=APIMigration.STAGE_RERANK)
    migration.add_calculator(calculator=factory.return_value_type_concepts_of_method2return_value_type_concepts_of_method_milvus_sim(),
                             name="return value type concepts of method->return value type concepts of method",
                             stage=APIMigration.STAGE_RERANK)
    migration.add_calculator(calculator=factory.functionalities_of_method2functionalities_of_method_milvus_sim(),
                             name="functionalities of method->functionalities of method",
                             stage=APIMigration.STAGE_RERANK)
    migration.add_calculator(calculator=factory.neighbor_concepts_of_method2neighbor_concepts_of_method_milvus_sim(),
                             name="neighbor concepts of method->neighbor concepts of method",
                             stage=APIMigration.STAGE_RERANK)

    return migration

def gene_temp_data(index, start, end):
    csv_path = os.path.join(DATA_DIR, 'query_data', 'APIMigrationBenchmark_method_{}.csv'.format(type))
    dataset = DataSet("method")
    dataset.load_from_csv(csv_path)
    library2methods = FileUtil.load_data_list(os.path.join(DATA_DIR, "icpc_saner", "all_library_method_dic_{}.json".format(type)))
    if type == "test":
        migration = create_method_pipeline(milvus=DBUtil.get_milvus(), neo4j_util=DBUtil.get_test_api_kg_util(), library2methods=library2methods, milvus_util=DBUtil.get_milvus_util())
    else:
        migration = create_method_pipeline(milvus=DBUtil.get_milvus(), neo4j_util=DBUtil.get_large_api_kg_util(), library2methods=library2methods, milvus_util=DBUtil.get_milvus_util())
    print(migration)
    final_retrieval_sim_collection = MultiCombineSimResultCollection()
    final_rerank_sim_collection = MultiCombineSimResultCollection()
    count = 0
    top_n = 100
    for ind, query_pair in enumerate(dataset.query_data):
        if ind < start or ind > end:
            continue

        temp_query_pair = [
            {"query_id": int(query_pair[dataset.position_a]), "target_id": int(query_pair[dataset.position_b])},
            {"query_id": int(query_pair[dataset.position_b]), "target_id": int(query_pair[dataset.position_a])}]
        for t in temp_query_pair:
            count = count + 1
            print("run node", time.time())
            print("thread", index, "complete ", count, str(t["query_id"]) + "_" + str(t["target_id"]))
            if filter == "":
                rerank_combine_sim_collection, retrieval_combine_sim_collection, complete_retrieval_combine_sim_collection = migration.run(
                    start_api_id=t["query_id"], retrieval_top_n=top_n, is_filter=True, rerank_top_n=top_n,
                    return_retrieval_result=True, is_complete=False)
            else:
                rerank_combine_sim_collection, retrieval_combine_sim_collection, complete_retrieval_combine_sim_collection = migration.run(
                    start_api_id=t["query_id"], retrieval_top_n=top_n, is_filter=True, rerank_top_n=top_n,
                    return_retrieval_result=True, is_complete=False, target_api_id=t["target_id"])

            final_retrieval_sim_collection.add(str(t["query_id"]) + "_" + str(t["target_id"]), retrieval_combine_sim_collection)
            final_rerank_sim_collection.add(str(t["query_id"]) + "_" + str(t["target_id"]), rerank_combine_sim_collection)
    final_retrieval_sim_collection.save(PathUtil.temp_multi_combine_sim_collection("{}_retrieve_method{}_model_{}".format(type, filter, str(index))))
    print("save {}_retrieve_method{}_model_{} success".format(type, filter, str(index)))
    final_rerank_sim_collection.save(PathUtil.temp_multi_combine_sim_collection("{}_rerank_method{}_model_{}".format(type, filter, str(index))))
    print("save {}_rerank_method{}_model_{} success".format(type, filter, str(index)))

def merge(thread_num):
    retrieve_result = None
    for index in range(thread_num):
        if retrieve_result is None:
            retrieve_result: MultiCombineSimResultCollection = MultiCombineSimResultCollection.load(PathUtil.temp_multi_combine_sim_collection("{}_retrieve_method{}_model_{}".format(type, filter, str(index+1))))
        else:
            retrieve: MultiCombineSimResultCollection = MultiCombineSimResultCollection.load(PathUtil.temp_multi_combine_sim_collection("{}_retrieve_method{}_model_{}".format(type, filter, str(index+1))))
            id2csrc = retrieve.id2name2sim_collection
            retrieve_result.id2name2sim_collection.update(id2csrc)

    rerank_result = None
    for index in range(thread_num):
        if rerank_result is None:
            rerank_result: MultiCombineSimResultCollection = MultiCombineSimResultCollection.load(PathUtil.temp_multi_combine_sim_collection("{}_rerank_method{}_model_{}".format(type, filter, str(index + 1))))

        else:
            rerank: MultiCombineSimResultCollection = MultiCombineSimResultCollection.load(PathUtil.temp_multi_combine_sim_collection("{}_rerank_method{}_model_{}".format(type, filter, str(index + 1))))
            id2csrc = rerank.id2name2sim_collection
            rerank_result.id2name2sim_collection.update(id2csrc)

    retrieve_result.save(PathUtil.multi_combine_sim_collection("{}_retrieve_method{}_model".format(type, filter)))
    print("save {}_retrieve_method{}_model success".format(type, filter))
    rerank_result.save(PathUtil.multi_combine_sim_collection("{}_rerank_method{}_model".format(type, filter)))
    print("save {}_rerank_method{}_model success".format(type, filter))


if __name__ == '__main__':
    time1 = time.time()
    # csv_path = os.path.join(DATA_DIR, 'query_data', 'APIMigrationBenchmark_method_{}.csv'.format(type))
    # dataset = DataSet("method")
    # dataset.load_from_csv(csv_path)
    # length = len(dataset.query_data)
    # batch_size = 500
    # batch_num = length // batch_size
    # if length % batch_size != 0:
    #     batch_num = batch_num + 1
    # threads = []
    # for index in range(batch_num):
    #     start = index * batch_size
    #     end = (index+1) * batch_size
    #
    #     threads.append(threading.Thread(
    #         target=gene_temp_data,
    #         args=(index+1, start, end)
    #     ))
    # # for t in threads:
    # #     t.start()
    # # for t in threads:
    # #     t.join()
    #
    # gene_temp_data(1, 0, 1000)
    #
    # merge(batch_num)
    #
    #


    time2 = time.time()
    '''
    ==============================================================================================================
    ==============================================================================================================
    '''

    # csv_path = os.path.join(DATA_DIR, 'query_data', 'APIMigrationBenchmark_method_{}.csv'.format(type))
    # dataset = DataSet("method")
    # dataset.load_from_csv(csv_path)

    # filter_top_n = 100
    # top_n = 100
    # top_n_list = [1, 3, 5, 10, 20, 30, 50, 100, 200]
    # se = SimEvaluator(top_n)

    # milvus = DBUtil.get_milvus()
    # eval_data_list = []
    #
    # retrieve: MultiCombineSimResultCollection = MultiCombineSimResultCollection.load(PathUtil.multi_combine_sim_collection("{}_retrieve_method{}_model".format(type, filter)))
    # rerank: MultiCombineSimResultCollection = MultiCombineSimResultCollection.load(PathUtil.multi_combine_sim_collection("{}_rerank_method{}_model".format(type, filter)))
    # retrieve_id2name2sim_collection = retrieve.id2name2sim_collection
    # rerank_id2name2sim_collection = rerank.id2name2sim_collection
    #
    # eval_result_list = []
    # count = 0
    #
    # name2weight = {
    #     "method->method": 0
    # }
    #
    # for name, weight in name2weight.items():
    #     name2weight[name] = 1
    #     try:
    #         se.evaluate(dataset=dataset, top_n_list=top_n_list, multi_combine_sim_result_collection=retrieve, combine_sim_result_collection_type="retrieve", msimcol_name="{}_retrieve_method{}_model".format(type, filter), name2weight=name2weight)
    #         count = count + 1
    #         print("evaluate: ", count)
    #         print(se.eval_result)
    #         eval_result_list.append(se.eval_result)
    #     except BaseException as e:
    #         print(e)
    #     name2weight[name] = 0
    #
    # name2weight = {
    #     "method->method": 1,
    # }
    #
    # rank_name2weight = {
    #     "class concepts of method->class concepts of method": 0,
    #     "parameter concepts of method->parameter concepts of method": 0,
    #     "parameter type concepts of method->parameter type concepts of method": 0,
    #     "return value type concepts of method->return value type concepts of method": 0,
    #     "functionalities of method->functionalities of method": 0,
    #     "neighbor concepts of method->neighbor concepts of method": 0,
    # }
    #
    # for name, weight in rank_name2weight.items():
    #     for n, w in rank_name2weight.items():
    #         name2weight[n] = 0
    #     name2weight[name] = 1
    #     try:
    #         se.evaluate(dataset=dataset, top_n_list=top_n_list, multi_combine_sim_result_collection=rerank, combine_sim_result_collection_type="rerank", msimcol_name="{}_rerank_method{}_model".format(type, filter), name2weight=name2weight)
    #         count = count + 1
    #         print("evaluate: ", count)
    #         print(se.eval_result)
    #         eval_result_list.append(se.eval_result)
    #     except BaseException as e:
    #         print(e)
    #     name2weight[name] = 0
    #
    # FileUtil.write2json(os.path.join(OUTPUT_DIR, "evaluate", "{}_method{}_evaluate.json".format(type, filter)), eval_result_list)
    # print("write {}_method{}_evaluate success".format(type, filter))
    time3 = time.time()
    '''
    ==============================================================================================================
    ==============================================================================================================
    '''
    top_n = 300
    namew2weight = {"method->method": 0.05,
                    "return value type concepts of method->return value type concepts of method": 0.05,
                    "functionalities of method->functionalities of method": 0.95,
                    "class concepts of method->class concepts of method": 0.8,
                    "parameter concepts of method->parameter concepts of method": 0.05,
                    "parameter type concepts of method->parameter type concepts of method": 0.25,
                    "neighbor concepts of method->neighbor concepts of method": 0.95}

    csv_path = os.path.join(DATA_DIR, 'query_data', 'APIMigrationBenchmark_method_{}.csv'.format(type))
    dataset = DataSet("method")
    dataset.load_from_csv(csv_path)
    milvus = DBUtil.get_milvus()
    if type == "test":
        graph_util = DBUtil.get_test_api_kg_util()
    else:
        graph_util = DBUtil.get_large_api_kg_util()
    milvus_util = MilvusUtil(milvus)

    rerank_combine_sim_collection: MultiCombineSimResultCollection = MultiCombineSimResultCollection.load(PathUtil.multi_combine_sim_collection("{}_2_rerank_method{}_model".format(type, filter)))

    result_list = []
    count = 0
    err_count = 0
    for query_pair in dataset.query_data:
        temp_query_pair = [
            {"query_id": int(query_pair[dataset.position_a]), "target_id": int(query_pair[dataset.position_b])},
            {"query_id": int(query_pair[dataset.position_b]), "target_id": int(query_pair[dataset.position_a])}

        ]
        for t in temp_query_pair:
            result = {"top_n": top_n}
            result["start_node_info"] = graph_util.get_node_by_id(t["query_id"])
            result["position"] = -1
            try:
                combine_results = rerank_combine_sim_collection.id2name2sim_collection[
                    str(t["query_id"]) + "_" + str(t["target_id"])].get_combine_sim_result(name2weight=namew2weight)
                result["combine_results"] = []
                for inde, te in enumerate(combine_results[:result["top_n"]]):
                    combine_result = {
                        "node_info": graph_util.get_node_by_id(te.end_id),
                        "score": te.score,
                        "extra": te.extra
                    }
                    result["combine_results"].append(combine_result)
                    if te.end_id == t["target_id"]:
                        result["position"] = inde
                count = count + 1
                err_count = err_count + 1
                print("process: ", count)
                result_list.append(result)
            except BaseException as e:
                print("error count: ", err_count, e)

    FileUtil.write2json(os.path.join(OUTPUT_DIR, "export_result", "{}_2_rerank_method{}_export_result.json".format(type, filter)), result_list)
    print("write ", "{}_2_rerank_method{}_export_result.json".format(type, filter), "success")
    time4 = time.time()

    print(time1)
    print(time2)
    print(time3)
    print(time4)



