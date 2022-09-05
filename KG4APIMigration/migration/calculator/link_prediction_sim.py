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

import numpy as np
import torch
from milvus import Milvus

from migration.calculator.base import SimResult
from migration.calculator.constant import Constant
from migration.calculator.milvussim import MilvusSim
from migration.converter.mapper import Node2NodeMapper, Node2VectorMapper
from migration.util.db_util import DBUtil
from migration.util.neo4j_util import Neo4jUtil
from migration.util.path_util import PathUtil


class ComplExLinkPredictionMilvusSim(MilvusSim):
    """
    基于链接预测的方式，计算相似度
    """

    MODE_START_NODE_AS_HEAD = 1
    MODE_START_NODE_AS_TAIL = 2

    def __init__(self, milvus_connection: Milvus,
                 collection_name: str = "migration_small_test",
                 partition_name: str = Constant.METHOD,
                 start_node_mapper: Node2NodeMapper = Node2NodeMapper(),
                 end_node_mapper: Node2NodeMapper = Node2NodeMapper(),
                 relation_embedding_path: str = PathUtil.complex_relation_file(),
                 relation_type="belong_to",
                 mode=MODE_START_NODE_AS_HEAD
                 ):
        """
        :param milvus_connection:
        :param collection_name:
        :param partition_name:
        :param start_node_mapper:
        :param end_node_mapper:
        :param relation_embedding_path: 关系向量的加载地址
        1. 直接用起始节点id的向量去找最相似的前N个，然后再注解计算mapper之后的相似度。
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

        self.relation2numpy_map = self.load_relation_embedding(relation_embedding_path)
        self.relation_type = relation_type
        self.mode = mode

    def complex_diagonal_dynamic_operator(self, embeddings, real_b, imag_b, dim):
        real_a = embeddings[..., : dim // 2]
        imag_a = embeddings[..., dim // 2:]
        prod = torch.empty_like(embeddings)
        prod[..., : dim // 2] = real_a * real_b - imag_a * imag_b
        prod[..., dim // 2:] = real_a * imag_b + imag_a * real_b
        return prod

    def dot_comparator(self, embedding1, embedding2):
        result = (embedding1 * embedding2).sum(-1)
        return result

    def load_relation_embedding(self, r_file=PathUtil.complex_relation_file()):
        """
        加载
        :param r_file:
        :return:
        """
        embeddings = np.loadtxt(
            r_file,
            dtype=np.float32,
            delimiter="\t",
            skiprows=0,
            max_rows=78404883,
            usecols=range(5, 5 + 128),
            comments=None,
        )

        relation2numpy_map = {}

        lines = []
        for line in open(r_file):
            line = line.strip()
            if len(line) == 0:
                continue
            # print(line)
            lines.append(line)

        for index, line in enumerate(lines):
            cols = line.split("\t")
            # print(cols)
            relation_name = cols[0]
            r_type = cols[1]
            part = cols[3]
            if relation_name not in relation2numpy_map:
                relation2numpy_map[relation_name] = {}
            if r_type not in relation2numpy_map[relation_name]:
                relation2numpy_map[relation_name][r_type] = {}
            if part not in relation2numpy_map[relation_name][r_type]:
                relation2numpy_map[relation_name][r_type][part] = {}

            relation2numpy_map[relation_name][r_type][part] = embeddings[index]

        return relation2numpy_map

    def batch_sim(self, start_api_id: int, top_n: int = 100) -> List[SimResult]:
        # todo: 去掉实体本身
        map_start_node_vector = self.start_node_vector_mapper.map(start_api_id)
        if len(map_start_node_vector) == 0:
            return []

        ids, distances = self.milvus_util.query_similar_vectors_ids_dis_by_vertors([map_start_node_vector],
                                                                                   self.collection_name,
                                                                                   self.partition_name,
                                                                                   top_n)

        return self.one_to_list_sim(start_api_id=start_api_id, end_api_id_list=ids)

    def matrix_sim(self, start_api_id_list: List[int], top_n: int = 500) -> List[List[SimResult]]:
        """
        todo: 需要实现一下，提高效率，比如查向量可以批量
        :param start_api_id_list:
        :param top_n:
        :return:
        """
        return [self.batch_sim(start_api_id, top_n) for start_api_id in start_api_id_list]

    def tuple_score(self, head_entity_id, relation_type, tail_entity_id):

        # get relation embedding
        relation_real = torch.from_numpy(self.relation2numpy_map[relation_type]["rhs"]["real"])
        relation_imag = torch.from_numpy(self.relation2numpy_map[relation_type]["rhs"]["imag"])

        # get entity embedding
        MU = DBUtil.get_milvus_util()
        embedding1 = torch.tensor(
            MU.query_vectors_by_ids(ids=[head_entity_id], collection_name=self.collection_name))
        embedding2 = torch.tensor(
            MU.query_vectors_by_ids(ids=[tail_entity_id], collection_name=self.collection_name))
        # operation
        operator_result = self.complex_diagonal_dynamic_operator(embedding2, relation_real, relation_imag, 256)

        # comparison
        pos_scores = self.dot_comparator(embedding1, operator_result)
        return pos_scores.item()

    def pair_sim(self, start_api_id, end_api_id) -> SimResult:
        map_start_id = self.start_node_vector_mapper.node2node_mapper.map(start_api_id)
        map_end_id = self.end_node_vector_mapper.node2node_mapper.map(end_api_id)
        score = 0
        if self.mode == self.MODE_START_NODE_AS_HEAD:
            score = self.tuple_score(head_entity_id=map_start_id, relation_type=self.relation_type,
                                     tail_entity_id=map_end_id)
        if self.mode == self.MODE_START_NODE_AS_TAIL:
            score = self.tuple_score(head_entity_id=map_end_id, relation_type=self.relation_type,
                                     tail_entity_id=map_start_id)
        return SimResult(start_api_id, end_api_id, score)

    def one_to_list_sim(self, start_api_id, end_api_id_list: List[int]) -> List[SimResult]:
        map_start_node_vector = self.start_node_vector_mapper.map(start_api_id)
        if len(map_start_node_vector) == 0:
            return [SimResult(start_api_id, end_api_id, 0) for end_api_id in end_api_id_list]
        # todo： 实现这个，其中可以批量获取end_api_id 对应的向量，并且可以批量计算一个向量和n个向量的距离
        results = [SimResult(start_id=start_api_id, end_id=end_id,
                             score=self.pair_sim(start_api_id=start_api_id, end_api_id=end_id))
                   for end_id in end_api_id_list]
        # print(results)
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

    sim_component = ComplExLinkPredictionMilvusSim(DBUtil.get_milvus(),
                                                   collection_name="migration_small_test",
                                                   partition_name=Constant.METHOD,
                                                   start_node_mapper=start_node2node_mapper,
                                                   end_node_mapper=end_node2node_mapper,
                                                   relation_type="belong_to"
                                                   )

    node = graph_util.get_node_by_id(test_id)
    print("start_node", node)
    results = sim_component.batch_sim(test_id)
    for index, t in enumerate(results[:200]):
        sim_node = graph_util.get_node_by_id(t.end_id)
        print(index + 1, sim_node)
        print(t)
        print("-" * 50)
    sim_collection = sim_component.batch_sim_collection(start_api_id=test_id)
    print(sim_collection)
