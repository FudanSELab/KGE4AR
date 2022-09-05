from unittest import TestCase

from migration.converter.mapper import Node2VectorMapper, Node2NodeMapper
from util.db_util import DBUtil


class TestNode2VectorMapper(TestCase):

    def test_self_map(self):
        test_cases = [(5597, 5597)]
        mapper = Node2NodeMapper(map_type=Node2NodeMapper.SELF_MAP)
        for test_id, correct_map_id in test_cases:
            node2vector_mapper = Node2VectorMapper(node2node_mapper=mapper,
                                                   milvus_util=DBUtil.get_milvus_util())
            vectors = node2vector_mapper.map(test_id)
            self.assertNotEqual(len(vectors), 0)
            print(vectors)

    def test_method2class_map(self):
        test_cases = [5597, 5639]
        mapper = Node2NodeMapper(map_type=Node2NodeMapper.METHOD_2_PARENT_CLASS)
        node2vector_mapper = Node2VectorMapper(node2node_mapper=mapper,
                                               milvus_util=DBUtil.get_milvus_util())
        for test_id in test_cases:
            vectors = node2vector_mapper.map(test_id)
            self.assertNotEqual(len(vectors), 0)
            print(vectors)

    def test_method2package_map(self):
        test_cases = [5597, 5639]
        mapper = Node2NodeMapper(map_type=Node2NodeMapper.METHOD_2_PARENT_PACKAGE)
        node2vector_mapper = Node2VectorMapper(node2node_mapper=mapper,
                                               milvus_util=DBUtil.get_milvus_util(),
                                               )
        for test_id in test_cases:
            vectors = node2vector_mapper.map(test_id)
            self.assertNotEqual(len(vectors), 0)
            print(vectors)

    def test_method2lib_map(self):
        test_cases = [5597, 5639]
        mapper = Node2NodeMapper(map_type=Node2NodeMapper.METHOD_2_PARENT_LIBRARY)
        node2vector_mapper = Node2VectorMapper(node2node_mapper=mapper,
                                               milvus_util=DBUtil.get_milvus_util())
        for test_id in test_cases:
            vectors = node2vector_mapper.map(test_id)
            self.assertNotEqual(len(vectors), 0)
            print(vectors)

    def test_method2parameter_type_map(self):
        test_cases = [5597, 5639]
        mapper = Node2NodeMapper(map_type=Node2NodeMapper.METHOD_2_PARAMETER_TYPE)
        node2vector_mapper = Node2VectorMapper(node2node_mapper=mapper,
                                               milvus_util=DBUtil.get_milvus_util())
        for test_id in test_cases:
            vectors = node2vector_mapper.map(test_id)
            # self.assertNotEqual(len(vectors), 0)
            print(vectors)
