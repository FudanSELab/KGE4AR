import time

from migration.util.db_util import DBUtil
from migration.util.milvus_util import MilvusUtil
from migration.util.neo4j_util import Neo4jUtil

from migration.calculator.base import SimCalculator, SimResult, CombineSimResultCollection, SimResultCollection
from migration.converter.filter import NodeFilter


class APIMigration:
    DEFAULT_RETRIEVAL_TOP_NUM = 1000
    DEFAULT_RERANK_TOP_NUM = 100
    # 目前计划分成两个阶段：retrieval + rerank，
    # retrieval ：前者负责筛选出相关的候选，简单相似度计算，多路召回
    # rerank ： 一对一相似度，更加精细的相似度计算与重排，比如在类级别算相似度
    STAGE_RETRIEVAL = "retrieval"
    STAGE_RERANK = "rerank"

    def __init__(self, graph_util: Neo4jUtil = DBUtil.get_test_api_kg_util(), library2methods: dict=None, milvus_util: MilvusUtil=None, big_or_small="small", vector_type=""):

        self.name2calculator = {}
        self.name2weight = {}
        self.node_filter = NodeFilter(graph_util)
        self.retrieval_calculator_name_list = set([])
        self.rerank_calculator_name_list = set([])
        self.library2methods = library2methods
        self.milvus_util = milvus_util
        self.big_or_small = big_or_small
        self.vector_type = vector_type

    def add_calculator(self, calculator: SimCalculator, name: str = None, weight: float = 1.0, stage=STAGE_RETRIEVAL):
        if not name:
            name = calculator.type()
        self.name2calculator[name] = calculator
        self.name2weight[name] = weight
        if stage == self.STAGE_RETRIEVAL:
            self.retrieval_calculator_name_list.add(name)

        if stage == self.STAGE_RERANK:
            self.rerank_calculator_name_list.add(name)

    def get_calculator_by_name(self, name):
        return self.name2calculator.get(name, None)

    def set_weight(self, name: str, weight):
        self.name2weight[name] = weight

    def get_weight(self, name: str):
        return self.name2weight.get(name, 0.0)

    def get_all_retrieval_calculator_names(self):
        return self.retrieval_calculator_name_list

    def get_all_rerank_calculator_names(self):
        return self.rerank_calculator_name_list

    def __repr__(self):
        return "APIMigration:" + str(
            [(name, type(self.name2calculator[name]), self.name2weight[name]) for name in self.name2calculator.keys()])

    def retrieval(self, start_api_id, top_n=DEFAULT_RETRIEVAL_TOP_NUM, is_filter=True, target_api_id=None) -> CombineSimResultCollection:
        """
        按照
        :param start_api_id:
        :param top_n:
        :param is_filter:
        :param target_api_id:
        :return:
        """
        combine_sim_collection = CombineSimResultCollection(start_id=start_api_id)
        if target_api_id is None:
            for name in self.get_all_retrieval_calculator_names():
                calculator = self.get_calculator_by_name(name)
                sim_collection = calculator.batch_sim_collection(start_api_id, top_n=top_n)
                print(name, calculator, start_api_id)
                before_filter = len(sim_collection)
                print("before filter=", before_filter)
                if is_filter:
                    sim_collection = self.node_filter.filter(start_api_id=start_api_id, combine_results=sim_collection)
                after_filter = len(sim_collection)
                print("after filter=", after_filter)
                combine_sim_collection.add_all_sim_result(name, sim_collection)
                combine_sim_collection.set_weight(name, self.get_weight(name))
                combine_sim_collection.set_filter_retention_num(name, {"before_filter": before_filter, "after_filter": after_filter})

            return combine_sim_collection

        else:
            combine_sim_collection = CombineSimResultCollection(start_id=start_api_id)
            node_id_list = []
            library_id = self.node_filter.neo4j_util.get_library_id_by_node_id(target_api_id)
            if library_id != -1:
                node_id_list = self.library2methods.get(str(library_id))
                if len(node_id_list) > 10000:
                    node_id_list = node_id_list[:5000]
            before_filter = len(node_id_list)
            print("before filter=", before_filter)
            after_filter = len(node_id_list)
            print("after filter=", after_filter)
            for id in node_id_list:
                score = self.milvus_util.calculate_distance_by_id(start_api_id, id, "migration_{}_test{}".format(self.big_or_small, self.vector_type), "method")
                sr = SimResult(start_api_id, id, score, None)
                combine_sim_collection.add_sim_result("method->method", sr)

            return combine_sim_collection


    def complete(self, start_api_id, combine_sim_result_collection: CombineSimResultCollection,
                 top_n=DEFAULT_RERANK_TOP_NUM) -> CombineSimResultCollection:
        complete_combine_sim_collection = CombineSimResultCollection(start_id=start_api_id)
        complete_combine_sim_collection.update(combine_sim_result_collection)

        combined_results = combine_sim_result_collection.get_combine_sim_result()
        for name in self.get_all_retrieval_calculator_names():
            calculator = self.get_calculator_by_name(name)
            exist_sim_collection: SimResultCollection = complete_combine_sim_collection.get_sim_collection(name=name)
            for index, t in enumerate(combined_results[:top_n]):
                end_api_id = t.end_id
                score = exist_sim_collection.get_score(end_id=end_api_id)
                if score != 0:
                    continue
                sim_result: SimResult = calculator.pair_sim(start_api_id, end_api_id)
                exist_sim_collection.add(sim_result)
        return complete_combine_sim_collection

    def rerank(self, start_api_id, combine_sim_result_collection: CombineSimResultCollection,
               top_n=DEFAULT_RERANK_TOP_NUM) -> CombineSimResultCollection:
        """
        按照上一步给定的结合各种相似度的结果，进行更加精细的计算，重排，主要都是一些点对点相似度
        :param combine_sim_result_collection: 上一步计算的各种相似度的缓存
        :param start_api_id:
        :param top_n: 只选择上一步的结果的多少进行重排
        :return:
        """
        rerank_combine_sim_collection = CombineSimResultCollection(start_id=start_api_id)
        combined_results = combine_sim_result_collection.get_combine_sim_result()
        rerank_combine_sim_collection.update(combine_sim_result_collection)

        # print("start pair", time.time())
        for name in self.get_all_rerank_calculator_names():
            calculator = self.get_calculator_by_name(name)
            sim_collection = SimResultCollection(start_id=start_api_id)

            for index, t in enumerate(combined_results[:top_n]):
                end_api_id = t.end_id
                sim_result: SimResult = calculator.pair_sim(start_api_id, end_api_id)
                sim_collection.add(sim_result)
            rerank_combine_sim_collection.add_all_sim_result(name, sim_collection)
            rerank_combine_sim_collection.set_weight(name, self.get_weight(name))
        # print("end pair", time.time())
        return rerank_combine_sim_collection

    def run(self, start_api_id,
            retrieval_top_n=DEFAULT_RETRIEVAL_TOP_NUM,
            is_filter=True,
            rerank_top_n=DEFAULT_RERANK_TOP_NUM,
            return_retrieval_result=False,
            is_complete=True,
            target_api_id=None):
        """
        对整个流水线，retrieval+rerank都跑一次
        :param return_retrieval_result, 是否将中间的retrieval的结果返回
        :param is_complete 是否将第一步retrieval的结果进行补全
        :return:
        """

        retrieval_combine_sim_collection = self.retrieval(start_api_id=start_api_id, top_n=retrieval_top_n,
                                                          is_filter=is_filter, target_api_id=target_api_id)
        if is_complete:

            complete_sim_collection = self.complete(start_api_id=start_api_id,
                                                    combine_sim_result_collection=retrieval_combine_sim_collection,
                                                    top_n=rerank_top_n)
        else:
            complete_sim_collection = retrieval_combine_sim_collection

        final_combine_sim_collection = self.rerank(start_api_id=start_api_id,
                                                   combine_sim_result_collection=complete_sim_collection,
                                                   top_n=rerank_top_n)

        if return_retrieval_result:
            return final_combine_sim_collection, retrieval_combine_sim_collection, complete_sim_collection
        else:
            return final_combine_sim_collection

    def filter_top_n(self, start_api_id, retrieve_combine_sim_result_collection: CombineSimResultCollection,
             rerank_combine_sim_result_collection: CombineSimResultCollection,
             top_n=100,
             name2weight:dict=None):

        sr_list = retrieve_combine_sim_result_collection.get_combine_sim_result(name2weight=name2weight)[:top_n]
        filter_rerank = CombineSimResultCollection(start_id=start_api_id)

        for name in rerank_combine_sim_result_collection.get_all_names():
            src: SimResultCollection = rerank_combine_sim_result_collection.get_sim_collection(name)
            for rsc in sr_list:
                filter_rerank.add_sim_result(name, SimResult(start_api_id, rsc.end_id, src.get_score(rsc.end_id)))

        return filter_rerank


