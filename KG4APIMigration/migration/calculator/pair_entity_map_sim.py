#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-----------------------------------------
@Author: isky
@Email: 19110240019@fudan.edu.cn
@Created: 2019/10/28
------------------------------------------
@Modify: 2019/10/28
------------------------------------------
@Description:
"""
from typing import List
from milvus import Milvus
from migration.calculator.base import SimResult
from migration.calculator.constant import Constant
from migration.calculator.milvussim import MilvusSim
from migration.converter.mapper import Node2NodeMapper
from migration.util.db_util import DBUtil
from migration.util.neo4j_util import Neo4jUtil


class EntityMappingMilvusSim(MilvusSim):
    MAP_MODE_MAP_START_NODE_BEFORE_BATCH_SIM = 1  # 使用原始id映射前的向量去计算第一轮候选相似节点
    MAP_MODE_MAP_START_NODE_AFTER_BATCH_SIM = 2  # 使用原始id映射后向量去计算第一轮候选相似节点
    """
    先基于起点计算批量相似度，确定可能相关的id节点，然后逐个计算pair sim。
    """

    def __init__(self, milvus_connection: Milvus,
                 collection_name: str = "migration_small_test",
                 partition_name: str = Constant.METHOD,
                 start_node2node_mapper: Node2NodeMapper = Node2NodeMapper(),
                 end_node2node_mapper: Node2NodeMapper = Node2NodeMapper(),
                 map_mode=MAP_MODE_MAP_START_NODE_BEFORE_BATCH_SIM
                 ):
        """
        :param milvus_connection:
        :param collection_name:
        :param partition_name:
        :param start_node2node_mapper:
        :param end_node2node_mapper:
        :param map_mode:
        1. 直接用起始节点id的向量去找最相似的前N个，然后再注解计算mapper之后的相似度。
        """
        super().__init__(milvus_connection)
        self.partition_name = partition_name
        self.collection_name = collection_name
        self.start_node2node_mapper = start_node2node_mapper
        self.end_node2node_mapper = end_node2node_mapper
        self.map_mode = map_mode

    def batch_sim(self, start_api_id: int, top_n: int = 100) -> List[SimResult]:
        map_start_api_id = self.start_node2node_mapper.map(start_api_id)
        if map_start_api_id == Node2NodeMapper.UNMAP_ID:
            return []
        ids = []
        distances = []
        if self.map_mode == self.MAP_MODE_MAP_START_NODE_BEFORE_BATCH_SIM:
            ids, distances = self.milvus_util.query_similar_vectors_ids_distances_by_ids([start_api_id],
                                                                                         self.collection_name,
                                                                                         self.partition_name,
                                                                                         top_n,
                                                                                         remove_self=True)
        if self.map_mode == self.MAP_MODE_MAP_START_NODE_AFTER_BATCH_SIM:
            ids, distances = self.milvus_util.query_similar_vectors_ids_distances_by_ids([map_start_api_id],
                                                                                         self.collection_name,
                                                                                         self.partition_name,
                                                                                         top_n,
                                                                                         remove_self=True)

        result = [SimResult(start_id=start_api_id, end_id=sim_id,
                            score=self.pair_sim(start_api_id=start_api_id, end_api_id=sim_id))
                  for sim_id, distance in
                  zip(ids, distances)]
        return result

    def matrix_sim(self, start_api_id_list: List[int], top_n: int = 500) -> List[List[SimResult]]:
        """
        todo: 需要实现一下，提高效率，比如查向量可以批量
        :param start_api_id_list:
        :param top_n:
        :return:
        """
        return [self.batch_sim(start_api_id, top_n) for start_api_id in start_api_id_list]

    def pair_sim(self, start_api_id, end_api_id) -> SimResult:
        map_start_api_id = self.start_node2node_mapper.map(start_api_id)
        if map_start_api_id == Node2NodeMapper.UNMAP_ID:
            return SimResult(start_api_id, end_api_id, 0)
        map_end_api_id = self.end_node2node_mapper.map(entity_id=end_api_id)

        score = self.milvus_util.calculate_distance_by_id(id_1=map_start_api_id,
                                                          id_2=map_end_api_id,
                                                          collection_name=self.collection_name)
        return SimResult(start_api_id, end_api_id, score)


if __name__ == "__main__":
    test_id = 5597
    graph = DBUtil.get_test_api_kg()
    graph_util = Neo4jUtil(graph)
    start_node2node_mapper = Node2NodeMapper(map_type=Node2NodeMapper.METHOD_2_PARENT_CLASS,
                                             neo4j_util=graph_util)
    end_node2node_mapper = Node2NodeMapper(map_type=Node2NodeMapper.METHOD_2_PARENT_CLASS,
                                           neo4j_util=graph_util)

    sim_component = EntityMappingMilvusSim(DBUtil.get_milvus(),
                                           collection_name="migration_small_test",
                                           partition_name=Constant.METHOD,
                                           start_node2node_mapper=start_node2node_mapper,
                                           end_node2node_mapper=end_node2node_mapper,
                                           map_mode=EntityMappingMilvusSim.MAP_MODE_MAP_START_NODE_BEFORE_BATCH_SIM
                                           )

    node = graph_util.get_node_by_id(test_id)
    print("start_node", node)
    results = sim_component.batch_sim(test_id)
    # print(results)
    for t in results[:10]:
        sim_node = graph_util.get_node_by_id(t.end_id)
        print(sim_node)

    sim_collection = sim_component.batch_sim_collection(start_api_id=test_id)
    print(sim_collection)
