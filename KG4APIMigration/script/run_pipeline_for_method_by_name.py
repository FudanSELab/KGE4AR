from migration.calculator.base import MultiCombineSimResultCollection
from migration.calculator.constant import Constant
from migration.calculator.factory import MilvusSimFactory
from migration.pipeline import APIMigration
from migration.util.db_util import DBUtil
from migration.util.path_util import PathUtil


def create_pipeline(milvus, neo4j_util):
    factory = MilvusSimFactory(milvus=milvus, neo4j_util=neo4j_util, collection_name="migration_small_test",
                               partition_name=Constant.METHOD)

    migration = APIMigration()
    migration.add_calculator(calculator=factory.method2method_milvus_sim(), name="method->method", weight=10)
    # migration.add_calculator(calculator=factory.class2method_milvus_sim(), name="class of method->method")
    # migration.add_calculator(calculator=factory.return_value2method_milvus_sim(), name="return value of method->method")
    # migration.add_calculator(calculator=factory.parameter2method_milvus_sim(), name="parameter of method->method")
    migration.add_calculator(calculator=factory.parents2method_milvus_sim(), name="parents of method->method")
    migration.add_calculator(calculator=factory.neighbours2method_milvus_sim(), name="neighbours of method->method")

    # 添加rerank模块
    migration.add_calculator(calculator=factory.class_of_method2class_of_method_milvus_sim(),
                             name="class of method->class of method", stage=APIMigration.STAGE_RERANK)
    migration.add_calculator(calculator=factory.return_value_of_method2return_value_of_method_milvus_sim(),
                             name="return value of method->return value of method", stage=APIMigration.STAGE_RERANK, )
    migration.add_calculator(calculator=factory.parameter_of_method2parameter_of_method_milvus_sim(),
                             name="parameters of method->parameters of method", stage=APIMigration.STAGE_RERANK)
    migration.add_calculator(calculator=factory.neighbors_of_method2neighbors_of_method_milvus_sim(),
                             name="neighbour of method->neighbour of method", stage=APIMigration.STAGE_RERANK)
    migration.add_calculator(calculator=factory.parents_of_method2parents_of_method_milvus_sim(),
                             name="parents of method->parents of method", stage=APIMigration.STAGE_RERANK)

    # 以下是新增的计算相似度的方法，通过链接预测来计算
    migration.add_calculator(calculator=factory.method_A_belong_to_class_of_method_B(),
                             name="method A->belong_to->class of method B", stage=APIMigration.STAGE_RERANK)
    migration.add_calculator(calculator=factory.method_B_belong_to_class_of_method_A(),
                             name="method B->belong_to->class of method A", stage=APIMigration.STAGE_RERANK)

    print(migration)
    return migration


if __name__ == "__main__":
    milvus = DBUtil.get_milvus()
    graph_util = DBUtil.get_test_api_kg_util()

    test_api_name_list = [
        "com.google.gson.JsonArray.size()",
        "org.json.JSONArray.length()",
        "org.apache.commons.io.IOUtils.readLines(java.io.InputStream)",
        "org.apache.commons.httpclient.HttpMethodBase.getURI()",
        "org.json.simple.JSONObject.toJSONString()",
        "org.json.JSONObject.getLong(java.lang.String)",
        "org.apache.commons.httpclient.HttpMethodBase.addRequestHeader(java.lang.String, java.lang.String)",
        "com.google.gson.stream.JsonWriter.beginObject()",
        "org.json.JSONWriter.object()"

    ]
    test_id_list = []

    for api_name in test_api_name_list:
        api_node_info = graph_util.get_node_by_qualified_name(api_name)
        api_id = api_node_info.get("id", -1)
        if api_id == -1:
            continue
        test_id_list.append(api_id)

    migration = create_pipeline(milvus=milvus, neo4j_util=graph_util)

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

        for index, t in enumerate(combine_results[:50]):
            sim_node = graph_util.get_node_by_id(t.end_id)
            print("rank-" + str(index + 1) + ":", t)
            print(sim_node)
            print("-" * 50)

        combine_results = complete_retrieval_combine_sim_collection.get_combine_sim_result()
        print("-retrieval complete" + "-" * 50)
        print(complete_retrieval_combine_sim_collection)

        for index, t in enumerate(combine_results[:50]):
            sim_node = graph_util.get_node_by_id(t.end_id)
            print("rank-" + str(index + 1) + ":", t)
            print(sim_node)
            print("-" * 50)

        combine_results = rerank_combine_sim_collection.get_combine_sim_result()
        print(rerank_combine_sim_collection)
        print("-rerank" + "-" * 50)

        # for t in results[:10]:
        for index, t in enumerate(combine_results[:50]):
            sim_node = graph_util.get_node_by_id(t.end_id)
            print("rank-" + str(index + 1) + ":", t)
            print(sim_node)
            print("-" * 50)

    final_retrieval_sim_collection.save(PathUtil.multi_combine_sim_collection("test_retrieval"))
    print(final_retrieval_sim_collection)
    final_complete_retrieval_sim_collection.save(PathUtil.multi_combine_sim_collection("test_retrieval_complete"))
    print(final_complete_retrieval_sim_collection)
    final_rerank_sim_collection.save(PathUtil.multi_combine_sim_collection("test_rerank"))
    print(final_rerank_sim_collection)
