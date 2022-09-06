#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import List
from milvus import Milvus
from migration.calculator.base import SimResult
from migration.calculator.constant import Constant
from migration.calculator.milvussim import MilvusSim
from migration.converter.mapper import Node2NodeMapper
from migration.util.db_util import DBUtil
from migration.util.neo4j_util import Neo4jUtil


class EntityMilvusSim(MilvusSim):
    def __init__(self, milvus_connection: Milvus,
                 collection_name: str = "migration_small_test",
                 partition_name: str = Constant.METHOD,
                 start_node_mapper: Node2NodeMapper = Node2NodeMapper()):
        super().__init__(milvus_connection)
        self.partition_name = partition_name
        self.collection_name = collection_name
        self.start_node_mapper = start_node_mapper

    def batch_sim(self, start_api_id: int, top_n: int = 100) -> List[SimResult]:


        map_start_api_id = self.start_node_mapper.map(start_api_id)
        if map_start_api_id == Node2NodeMapper.UNMAP_ID:
            return []
        ids, distances = self.milvus_util.query_similar_vectors_ids_distances_by_ids([map_start_api_id],
                                                                                     self.collection_name,
                                                                                     self.partition_name,
                                                                                     top_n,
                                                                                     remove_self=True)

        result = [SimResult(start_id=start_api_id, end_id=sim_id, score=distance) for sim_id, distance in
                  zip(ids, distances)]
        return result

    def matrix_sim(self, start_api_id_list: List[int], top_n: int = 500) -> List[List[SimResult]]:
        return [self.batch_sim(start_api_id, top_n) for start_api_id in start_api_id_list]

    def pair_sim(self, start_api_id, end_api_id) -> SimResult:
        map_start_api_id = self.start_node_mapper.map(start_api_id)
        if map_start_api_id == Node2NodeMapper.UNMAP_ID:
            return SimResult(start_api_id, end_api_id, 0)

        score = self.milvus_util.calculate_distance_by_id(id_1=map_start_api_id,
                                                          id_2=end_api_id,
                                                          collection_name=self.collection_name)
        return SimResult(start_api_id, end_api_id, score)


if __name__ == "__main__":
    test_id = 5597
    sim_component = EntityMilvusSim(DBUtil.get_milvus())
    graph = DBUtil.get_test_api_kg()
    graph_util = Neo4jUtil(graph)
    node = graph_util.get_node_by_id(test_id)
    print("start_node", node)
    results = sim_component.batch_sim(test_id)
    # print(results)
    for t in results[:10]:
        sim_node = graph_util.get_node_by_id(t.end_id)
        print(sim_node)

    sim_collection = sim_component.batch_sim_collection(start_api_id=test_id)
    print(sim_collection)
