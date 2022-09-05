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


class AverageEntityMilvusSim(MilvusSim):
    def __init__(self, milvus_connection: Milvus,
                 collection_name: str = "migration_small_test",
                 partition_name: str = Constant.METHOD,
                 node2node_mapper: Node2NodeMapper = Node2NodeMapper(Node2NodeMapper.METHOD_2_PARAMETERS_TYPE)):
        super().__init__(milvus_connection)
        self.partition_name = partition_name
        self.collection_name = collection_name
        self.node2node_mapper = node2node_mapper

    def batch_sim(self, start_api_id: int, top_n: int = 100) -> List[SimResult]:
        map_start_api_ids = self.node2node_mapper.multi_map(start_api_id)

        if len(map_start_api_ids) == 0:
            return []
        a_nei_vectors = self.milvus_util.query_vectors_by_ids(map_start_api_ids,
                                                              self.collection_name,
                                                              self.partition_name,
                                                              top_n,
                                                              remove_self=True)

        a_avg_nei_vector = self.milvus_util.average(a_nei_vectors)
        ids, distances = self.milvus_util.query_similar_vectors_ids_dis_by_vertors(
            [a_avg_nei_vector],
            self.collection_name,
            self.partition_name,
            top_n)

        result = [SimResult(start_id=start_api_id, end_id=sim_id, score=distance) for sim_id, distance in
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
        return SimResult(start_api_id, end_api_id, 0)


if __name__ == "__main__":
    test_id = 5639
    sim_component = AverageEntityMilvusSim(DBUtil.get_milvus())
    graph = DBUtil.get_test_api_kg()
    graph_util = Neo4jUtil(graph)
    node = graph_util.get_node_by_id(test_id)
    print("start_node", node)
    results = sim_component.batch_sim(test_id)
    for t in results[:10]:
        sim_node = graph_util.get_node_by_id(t.end_id)
        print(sim_node)

    sim_collection = sim_component.batch_sim_collection(start_api_id=test_id)
    print(sim_collection)
