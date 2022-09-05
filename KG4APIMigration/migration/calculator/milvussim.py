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
from migration.calculator.base import SimCalculator, SimResult
from migration.util.db_util import DBUtil
from migration.util.milvus_util import MilvusUtil
from migration.util.neo4j_util import Neo4jUtil


class MilvusSim(SimCalculator):
    def __init__(self, milvus_connection: Milvus):
        super().__init__()
        self.milvus_util = None
        self.milvus_connection = None
        self.set_milvus_connection(milvus_connection)

    def set_milvus_connection(self, milvus_connection):
        self.milvus_connection = milvus_connection
        self.milvus_util = MilvusUtil(milvus_connection)

    def batch_sim(self, start_api_id, top_n=500) -> List[SimResult]:
        result = [SimResult(start_id=start_api_id, end_id=i, score=0.7) for i in range(0, top_n)]
        return result

    def pair_sim(self, start_api_id, end_api_id)->SimResult:
        return SimResult(start_api_id, end_api_id, 0.7)


if __name__ == "__main__":
    test_id = 5597
    sim_component = MilvusSim(DBUtil.get_milvus())
    graph = DBUtil.get_test_api_kg()
    graph_util = Neo4jUtil(graph)
    node = graph_util.get_node_by_id(test_id)
    print("start_node", node)
    result = sim_component.batch_sim(test_id)
    print(result)
