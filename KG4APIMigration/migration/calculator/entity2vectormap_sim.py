#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import List
from milvus import Milvus
from migration.calculator.base import SimResult
from migration.calculator.constant import Constant
from migration.calculator.milvussim import MilvusSim
from migration.converter.mapper import Node2NodeMapper, Node2VectorMapper
from migration.util.db_util import DBUtil
from migration.util.neo4j_util import Neo4jUtil


class Entity2VectorMappingMilvusSim(MilvusSim):

    def __init__(self, milvus_connection: Milvus,
                 collection_name: str = "migration_test_2",
                 partition_name: str = Constant.METHOD,
                 start_node_mapper: Node2NodeMapper = Node2NodeMapper(),
                 end_node_mapper: Node2NodeMapper = Node2NodeMapper(),
                 ):
        """
        :param milvus_connection:
        :param collection_name:
        :param partition_name:
        :param start_node_mapper:
        :param end_node_mapper:
        :param map_mode:

        """
        super().__init__(milvus_connection)
        self.partition_name = partition_name
        self.collection_name = collection_name
        # self.start_node_mapper = start_node_mapper
        self.start_node_vector_mapper = Node2VectorMapper(
            milvus_util=self.milvus_util,
            collection_name=collection_name,
            node2node_mapper=start_node_mapper
        )
        # self.end_node_mapper = end_node_mapper
        self.end_node_vector_mapper = Node2VectorMapper(
            milvus_util=self.milvus_util,
            collection_name=collection_name,
            node2node_mapper=end_node_mapper
        )

    def batch_sim(self, start_api_id: int, top_n: int = 100) -> List[SimResult]:
        map_start_node_vector = self.start_node_vector_mapper.map(start_api_id)
        if len(map_start_node_vector) == 0:
            return []

        ids, distances = self.milvus_util.query_similar_vectors_ids_dis_by_vertors([map_start_node_vector],
                                                                                   self.collection_name,
                                                                                   self.partition_name,
                                                                                   top_n,
                                                                                   remove_self=False)

        if self.end_node_vector_mapper.is_self_map():
            # 相当于对于终点不进行变化，那么直接可以用milvus的批量跑出的距离结果
            return [SimResult(start_id=start_api_id, end_id=sim_id,
                              score=distance) for sim_id, distance in zip(ids, distances)]
        else:
            # 对于终点进行变化，那么直接可以用milvus的批量跑出的距离确定相似id候选，然后再使用pair sim仔细地每一个候选计算变化之后的相似度
            return self.one_to_list_sim(start_api_id=start_api_id, end_api_id_list=ids)

    def matrix_sim(self, start_api_id_list: List[int], top_n: int = 500) -> List[List[SimResult]]:
        """
        :param start_api_id_list:
        :param top_n:
        :return:
        """
        return [self.batch_sim(start_api_id, top_n) for start_api_id in start_api_id_list]

    def pair_sim(self, start_api_id, end_api_id) -> SimResult:
        map_start_node_vector = self.start_node_vector_mapper.map(start_api_id)
        if len(map_start_node_vector) == 0:
            return SimResult(start_api_id, end_api_id, 0)

        map_end_node_vector = self.end_node_vector_mapper.map(end_api_id)
        if len(map_end_node_vector) == 0:
            return SimResult(start_api_id, end_api_id, 0)

        score = self.milvus_util.calculate_distance(map_start_node_vector,
                                                    map_end_node_vector)
        return SimResult(start_api_id, end_api_id, score)


    # def batch_one_to_list_sim(self, start_api_id, end_api_id_list: List[id]):
    #     map_start_node_vector = self.start_node_vector_mapper.map(start_api_id)
    #     if len(map_start_node_vector) == 0:
    #         return [SimResult(start_api_id, end_api_id, 0) for end_api_id in end_api_id_list]
    #     results = []
    #     end_api_id_vectors = []
    #     temp_end_api_id_list = []
    #     for end_api_id in end_api_id_list:
    #         end_api_id_vector = self.end_node_vector_mapper.map(end_api_id)
    #         if len(end_api_id_vector) == 0:
    #             results.append(SimResult(start_api_id, end_api_id, 0))
    #         else:
    #             end_api_id_vectors.append(self.end_node_vector_mapper.map(end_api_id))
    #             temp_end_api_id_list.append(end_api_id)
    #     all_scores = self.milvus_util.batch_calculate_distance(map_start_node_vector, end_api_id_vectors)
    #     for index, temp_end_api_id in enumerate(temp_end_api_id_list):
    #         results.append(SimResult(start_api_id, temp_end_api_id, all_scores[index]))
    #     results = sorted(results, key=lambda x: x.score, reverse=True)
    #     return results

    def one_to_list_sim(self, start_api_id, end_api_id_list: List[int]) -> List[SimResult]:
        map_start_node_vector = self.start_node_vector_mapper.map(start_api_id)
        if len(map_start_node_vector) == 0:
            return [SimResult(start_api_id, end_api_id, 0) for end_api_id in end_api_id_list]
        results = [SimResult(start_id=start_api_id, end_id=end_id,
                             score=self.pair_sim(start_api_id=start_api_id, end_api_id=end_id))
                   for end_id in end_api_id_list]

        results = sorted(results, key=lambda x: x.score, reverse=True)
        return results


class Entity2MaxVectorMappingMilvusSim(MilvusSim):

    def __init__(self, milvus_connection: Milvus,
                 collection_name: str = "migration_test_2",
                 partition_name: str = Constant.METHOD,
                 start_node_mapper: Node2NodeMapper = Node2NodeMapper(),
                 end_node_mapper: Node2NodeMapper = Node2NodeMapper(),
                 ):
        """
        :param milvus_connection:
        :param collection_name:
        :param partition_name:
        :param start_node_mapper:
        :param end_node_mapper:
        :param map_mode:
        """
        super().__init__(milvus_connection)
        self.partition_name = partition_name
        self.collection_name = collection_name
        # self.start_node_mapper = start_node_mapper
        self.start_node_vector_mapper = Node2VectorMapper(
            milvus_util=self.milvus_util,
            collection_name=collection_name,
            node2node_mapper=start_node_mapper
        )
        # self.end_node_mapper = end_node_mapper
        self.end_node_vector_mapper = Node2VectorMapper(
            milvus_util=self.milvus_util,
            collection_name=collection_name,
            node2node_mapper=end_node_mapper
        )

    def batch_sim(self, start_api_id: int, top_n: int = 100) -> List[SimResult]:
        map_start_node_vector = self.start_node_vector_mapper.map(start_api_id)
        if len(map_start_node_vector) == 0:
            return []

        ids, distances = self.milvus_util.query_similar_vectors_ids_dis_by_vertors([map_start_node_vector],
                                                                                   self.collection_name,
                                                                                   self.partition_name,
                                                                                   top_n,
                                                                                   remove_self=False)

        if self.end_node_vector_mapper.is_self_map():
            # 相当于对于终点不进行变化，那么直接可以用milvus的批量跑出的距离结果
            return [SimResult(start_id=start_api_id, end_id=sim_id,
                              score=distance) for sim_id, distance in zip(ids, distances)]
        else:
            # 对于终点进行变化，那么直接可以用milvus的批量跑出的距离确定相似id候选，然后再使用pair sim仔细地每一个候选计算变化之后的相似度
            return self.one_to_list_sim(start_api_id=start_api_id, end_api_id_list=ids)

    def matrix_sim(self, start_api_id_list: List[int], top_n: int = 500) -> List[List[SimResult]]:
        """
        :param start_api_id_list:
        :param top_n:
        :return:
        """
        return [self.batch_sim(start_api_id, top_n) for start_api_id in start_api_id_list]

    def pair_sim(self, start_api_id, end_api_id) -> SimResult:
        map_start_nodes = self.start_node_vector_mapper.node2node_mapper.unify_map(entity_id=start_api_id)
        if len(map_start_nodes) == 0:
            return SimResult(start_api_id, end_api_id, 0)

        map_end_nodes = self.end_node_vector_mapper.node2node_mapper.unify_map(entity_id=end_api_id)
        if len(map_end_nodes) == 0:
            return SimResult(start_api_id, end_api_id, 0)

        max_score = 0
        for n1 in map_start_nodes:
            for n2 in map_end_nodes:
                score = self.milvus_util.calculate_distance_by_id(n1, n2, self.collection_name)
                if score > max_score:
                    max_score = score
        return SimResult(start_api_id, end_api_id, max_score)


    def one_to_list_sim(self, start_api_id, end_api_id_list: List[int]) -> List[SimResult]:
        map_start_node_vector = self.start_node_vector_mapper.map(start_api_id)
        if len(map_start_node_vector) == 0:
            return [SimResult(start_api_id, end_api_id, 0) for end_api_id in end_api_id_list]
        results = [SimResult(start_id=start_api_id, end_id=end_id,
                             score=self.pair_sim(start_api_id=start_api_id, end_api_id=end_id))
                   for end_id in end_api_id_list]

        results = sorted(results, key=lambda x: x.score, reverse=True)
        return results


if __name__ == "__main__":
    test_id = 5597
    graph = DBUtil.get_test_api_kg()
    graph_util = Neo4jUtil(graph)
    start_node2node_mapper = Node2NodeMapper(map_type=Node2NodeMapper.SELF_MAP,
                                             neo4j_util=graph_util)
    end_node2node_mapper = Node2NodeMapper(map_type=Node2NodeMapper.METHOD_2_PARENT_CLASS,
                                           neo4j_util=graph_util)

    sim_component = Entity2VectorMappingMilvusSim(DBUtil.get_milvus(),
                                                  collection_name="migration_small_test",
                                                  partition_name=Constant.METHOD,
                                                  start_node_mapper=start_node2node_mapper,
                                                  end_node_mapper=end_node2node_mapper,
                                                  )

    node = graph_util.get_node_by_id(test_id)
    print("start_node", node)
    results = sim_component.batch_sim(test_id)
    for index, t in enumerate(results[:20]):
        sim_node = graph_util.get_node_by_id(t.end_id)
        print(index + 1, sim_node)
        print(t)
        print("-" * 50)
    sim_collection = sim_component.batch_sim_collection(start_api_id=test_id)
    print(sim_collection)
