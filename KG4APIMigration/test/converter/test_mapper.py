from unittest import TestCase

from migration.converter.mapper import Node2NodeMapper


class TestNode2NodeMapper(TestCase):
    def test_self_map(self):
        test_cases = [(5597, 5597)]
        mapper = Node2NodeMapper(map_type=Node2NodeMapper.SELF_MAP)
        for test_id, correct_map_id in test_cases:
            map_id = mapper.map(entity_id=test_id)
            self.assertEqual(map_id, correct_map_id)

    def test_method2class_map(self):
        test_cases = [(5597, Node2NodeMapper.UNMAP_ID), (5639, Node2NodeMapper.UNMAP_ID)]
        mapper = Node2NodeMapper(map_type=Node2NodeMapper.METHOD_2_PARENT_CLASS)
        for test_id, incorrect_map_id in test_cases:
            map_id = mapper.map(entity_id=test_id)
            print(map_id)
            self.assertNotEqual(map_id, incorrect_map_id)

    def test_method2package_map(self):
        test_cases = [(5597, Node2NodeMapper.UNMAP_ID)]
        mapper = Node2NodeMapper(map_type=Node2NodeMapper.METHOD_2_PARENT_PACKAGE)
        for test_id, incorrect_map_id in test_cases:
            map_id = mapper.map(entity_id=test_id)
            print(map_id)
            self.assertNotEqual(map_id, incorrect_map_id)

    def test_method2lib_map(self):
        test_cases = [(5597, Node2NodeMapper.UNMAP_ID)]
        mapper = Node2NodeMapper(map_type=Node2NodeMapper.METHOD_2_PARENT_LIBRARY)
        for test_id, incorrect_map_id in test_cases:
            map_id = mapper.map(entity_id=test_id)
            print(map_id)
            self.assertNotEqual(map_id, incorrect_map_id)

    def test_method2parameter_type_map(self):
        test_cases = [(4474, 0), (5639, 0)]
        mapper = Node2NodeMapper(map_type=Node2NodeMapper.METHOD_2_PARAMETER_TYPE)
        for test_id, incorrect_map_id in test_cases:
            map_ids = mapper.multi_map(entity_id=test_id)
            print(map_ids)
            self.assertNotEqual(len(map_ids), incorrect_map_id)
