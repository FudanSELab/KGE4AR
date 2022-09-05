import time
from migration.calculator.base import MultiCombineSimResultCollection
from migration.calculator.constant import Constant
from migration.calculator.factory import MilvusSimFactory
from migration.calculator.link_prediction_sim import ComplExLinkPredictionMilvusSim
from migration.converter.mapper import Node2NodeMapper
from migration.pipeline import APIMigration
from migration.util.db_util import DBUtil
from migration.util.path_util import PathUtil


def create_method_pipeline(milvus, neo4j_util):
    factory = MilvusSimFactory(milvus=milvus, neo4j_util=neo4j_util, collection_name="migration_small_test", partition_name=Constant.METHOD)

    migration = APIMigration()
    migration.add_calculator(calculator=factory.method2method_milvus_sim(), name="method->method")
    migration.add_calculator(calculator=factory.class2method_milvus_sim(), name="class->method")
    migration.add_calculator(calculator=factory.neighbours2method_milvus_sim(), name="neighbours->method")

    # 添加rerank模块
    migration.add_calculator(calculator=factory.class_of_method2class_of_method_milvus_sim(), name="class of method->class of method", stage=APIMigration.STAGE_RERANK)
    migration.add_calculator(calculator=factory.package_of_method2package_of_method_milvus_sim(), name="package of method->package of method", stage=APIMigration.STAGE_RERANK)
    migration.add_calculator(calculator=factory.neighbors_of_method2neighbors_of_method_milvus_sim(), name="neighbour of method->neighbour of method", stage=APIMigration.STAGE_RERANK)
    migration.add_calculator(calculator=factory.parents_of_method2parents_of_method_milvus_sim(), name="parents of method->parents of method", stage=APIMigration.STAGE_RERANK)
    migration.add_calculator(calculator=factory.method_A_belong_to_class_of_method_B(), name="method A->belong_to->class of method B", stage=APIMigration.STAGE_RERANK)
    migration.add_calculator(calculator=factory.method_B_belong_to_class_of_method_A(), name="method B->belong_to->class of method A", stage=APIMigration.STAGE_RERANK)

    return migration


if __name__ == "__main__":
    # test_id = 889000 # com.google.gson.JsonArray.size()=>org.json.JSONArray.length()
    # test_id = 219692 # org.apache.commons.io.IOUtils.readLines(java.io.InputStream)
    # test_id = 207758 # org.apache.commons.httpclient.HttpMethodBase.getURI()
    # test_id = 309495 # org.json.simple.JSONObject.toJSONString()

    # test_id = 5639  # org.apache.commons.httpclient.HttpMethodBase.addRequestHeader(java.lang.String, java.lang.String)

    test_id_list = [185705, 185957, 185486]

    milvus = DBUtil.get_milvus()
    graph_util = DBUtil.get_test_api_kg_util()
    migration = create_method_pipeline(milvus=milvus, neo4j_util=graph_util)

    final_retrieval_sim_collection = MultiCombineSimResultCollection()
    final_complete_retrieval_sim_collection = MultiCombineSimResultCollection()
    final_rerank_sim_collection = MultiCombineSimResultCollection()

    for test_id in test_id_list:
        start_node_info = graph_util.get_node_by_id(test_id)
        print("start_node", start_node_info)
        rerank_combine_sim_collection, retrieval_combine_sim_collection, complete_retrieval_combine_sim_collection = migration.run(
            test_id,
            retrieval_top_n=1000,
            rerank_top_n=100,
            return_retrieval_result=True)
        final_retrieval_sim_collection.add(api_id=test_id, combine_sim_collection=retrieval_combine_sim_collection)
        final_complete_retrieval_sim_collection.add(api_id=test_id,
                                                    combine_sim_collection=complete_retrieval_combine_sim_collection)
        final_rerank_sim_collection.add(api_id=test_id, combine_sim_collection=rerank_combine_sim_collection)

        combine_results = retrieval_combine_sim_collection.get_combine_sim_result()
        print("-retrieval" + "-" * 50)
        print(retrieval_combine_sim_collection)

        for index, t in enumerate(combine_results[:20]):
            sim_node = graph_util.get_node_by_id(t.end_id)
            print("rank-" + str(index + 1) + ":", t)
            print(sim_node)
            print("-" * 50)

        combine_results = complete_retrieval_combine_sim_collection.get_combine_sim_result()
        print("-retrieval complete" + "-" * 50)
        print(complete_retrieval_combine_sim_collection)

        for index, t in enumerate(combine_results[:20]):
            sim_node = graph_util.get_node_by_id(t.end_id)
            print("rank-" + str(index + 1) + ":", t)
            print(sim_node)
            print("-" * 50)

        combine_results = rerank_combine_sim_collection.get_combine_sim_result()
        print(rerank_combine_sim_collection)
        print("-rerank" + "-" * 50)

        # for t in results[:10]:
        for index, t in enumerate(combine_results[:20]):
            sim_node = graph_util.get_node_by_id(t.end_id)
            print("rank-" + str(index + 1) + ":", t)
            print(sim_node)
            print("-" * 50)

