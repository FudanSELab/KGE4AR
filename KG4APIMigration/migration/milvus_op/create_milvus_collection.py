# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-----------------------------------------
@Author: zz
@Email: 21212010059@m.fudan.edu.cn
@Created: 2022/06/15
------------------------------------------
@Modify: 2022/06/15
------------------------------------------
@Description:
"""
from milvus import Milvus, MetricType, IndexType
from py2neo import Graph

class CreateMilvusCollection():
    def __init__(self):
        self.milvus = Milvus(host='10.176.34.89', port='19530')
        self.graph = Graph("bolt://10.176.64.33:9123", user="neo4j", password="fdsefdse")

    def creat_index(self, collection_name):
        print("start create index for: ", collection_name)
        ivf_param = {'nlist': 16384}
        re = self.milvus.create_index(collection_name, IndexType.IVF_FLAT, ivf_param)
        try:
            print(re)
        except:
            print("error----")
        print("end create index for: ", collection_name)

    def create_collection(self, collection_name):
        param = {'collection_name': collection_name, 'dimension': 256,
                 'index_file_size': 1024, 'metric_type': MetricType.IP}
        print(self.milvus.create_collection(param))

    def drop_collection(self, collection_name):
        print(self.milvus.drop_collection(collection_name))

    def create_partition(self, collection_name, partition_name):
        print(self.milvus.create_partition(collection_name, partition_name))

    def drop_partition(self, collection_name, partition_name):
        print(self.milvus.drop_partition(collection_name, partition_name))



if __name__ == '__main__':

    collection_name = "migration_small_test_without_functionality_concept"
    cmc = CreateMilvusCollection()
    cmc.drop_collection(collection_name)
    cmc.create_collection(collection_name)
    cmc.create_partition(collection_name, "method")
    cmc.create_partition(collection_name, "package")
    cmc.create_partition(collection_name, "class")
    cmc.create_partition(collection_name, "library")
    cmc.create_partition(collection_name, "parameter")
    cmc.create_partition(collection_name, "return_value")
    cmc.create_partition(collection_name, "concept")
    cmc.create_partition(collection_name, "method_desc_include_functionality")
    cmc.create_partition(collection_name, "method_name_include_functionality")
    cmc.create_partition(collection_name, "func_verb")



