import time
from typing import List

from migration.util.db_util import DBUtil
from migration.util.milvus_util import MilvusUtil
from migration.util.neo4j_util import Neo4jUtil


class Node2NodeMapper:

    SELF_MAP = 0
    METHOD_2_PARENT_CLASS = 1
    METHOD_2_PARENT_PACKAGE = 2
    METHOD_2_PARENT_LIBRARY = 3
    METHOD_2_RETURN_VALUE_TYPE = 4
    METHOD_2_RETURN_VALUE = 5
    METHOD_2_PARENTS = 6
    METHOD_2_NEIGHBOURS = 7
    METHOD_2_NEIGHBOUR_WITH_CONCEPTS = 8
    METHOD_2_NEIGHBOUR_CONCEPTS = 9
    METHOD_2_PARAMETER_TYPES = 10
    METHOD_2_PARAMETERS = 11
    METHOD_2_CONCEPTS = 12
    METHOD_2_FUNCTIONALITIES = 13
    METHOD_2_FUNCTIONALITY_CONCEPTS = 14
    METHOD_2_FUNC_VERB = 15
    METHOD_2_NEIGHBOUR_WITH_FUNC_VERBS = 16
    METHOD_2_NEIGHBOUR_WITH_FUNCTIONALITIES = 17
    METHOD_2_NEIGHBOUR_WITH_FUNC_VERBS_FUNCTIONALITIES_CONCEPTS = 18
    METHOD_2_CLASS_CONCEPTS = 19
    METHOD_2_PARAMETER_CONCEPTS = 20
    METHOD_2_PARAMETER_TYPE_CONCEPTS = 21
    METHOD_2_RETURN_VALUE_TYPE_CONCEPTS = 22

    CLASS_2_PARENT_PACKAGE = 23
    CLASS_2_PARENT_LIBRARY = 24
    CLASS_2_EXTENDS_CLASS = 25
    CLASS_2_PARENTS = 26
    CLASS_2_NEIGHBOURS = 27
    CLASS_2_METHODS = 28
    CLASS_2_IMPLEMENTS_INTERFACES = 29

    UNMAP_ID = -1

    def __init__(self, map_type=SELF_MAP, neo4j_util: Neo4jUtil=DBUtil.get_test_api_kg_util()):
        self.map_type = map_type
        self.neo4j_util = neo4j_util
        self.single_map_types = {
            self.SELF_MAP,
            self.METHOD_2_PARENT_CLASS,
            self.METHOD_2_PARENT_PACKAGE,
            self.METHOD_2_PARENT_LIBRARY,
            self.METHOD_2_RETURN_VALUE_TYPE,
            self.METHOD_2_RETURN_VALUE,
            self.METHOD_2_FUNC_VERB,
            self.CLASS_2_PARENT_PACKAGE,
            self.CLASS_2_PARENT_LIBRARY,
            self.CLASS_2_EXTENDS_CLASS,

        }
        self.multi_map_types = {
            self.METHOD_2_PARAMETER_TYPES,
            self.METHOD_2_NEIGHBOURS,
            self.METHOD_2_NEIGHBOUR_WITH_CONCEPTS,
            self.METHOD_2_NEIGHBOUR_CONCEPTS,
            self.METHOD_2_PARENTS,
            self.METHOD_2_PARAMETERS,
            self.METHOD_2_CONCEPTS,
            self.METHOD_2_FUNCTIONALITIES,
            self.METHOD_2_FUNCTIONALITY_CONCEPTS,
            self.METHOD_2_NEIGHBOUR_WITH_FUNCTIONALITIES,
            self.METHOD_2_NEIGHBOUR_WITH_FUNC_VERBS,
            self.METHOD_2_NEIGHBOUR_WITH_FUNC_VERBS_FUNCTIONALITIES_CONCEPTS,
            self.METHOD_2_CLASS_CONCEPTS,
            self.METHOD_2_RETURN_VALUE_TYPE_CONCEPTS,
            self.METHOD_2_PARAMETER_CONCEPTS,
            self.METHOD_2_PARAMETER_TYPE_CONCEPTS,
            self.CLASS_2_PARENTS,
            self.CLASS_2_METHODS,
            self.CLASS_2_NEIGHBOURS,
            self.CLASS_2_IMPLEMENTS_INTERFACES,
        }

    def is_self_map(self):
        if self.map_type == self.SELF_MAP:
            return True
        return False

    def map(self, entity_id: int) -> int:
        if self.map_type == self.SELF_MAP:
            return entity_id
        if self.map_type == self.METHOD_2_PARENT_CLASS:
            return self.neo4j_util.get_class_of_method(start_id=entity_id)
        if self.map_type == self.METHOD_2_PARENT_PACKAGE:
            return self.neo4j_util.get_package_of_method(start_id=entity_id)
        if self.map_type == self.METHOD_2_PARENT_LIBRARY:
            return self.neo4j_util.get_library_of_method(start_id=entity_id)
        if self.map_type == self.METHOD_2_RETURN_VALUE_TYPE:
            return self.neo4j_util.get_return_value_type_of_method(start_id=entity_id)
        if self.map_type == self.METHOD_2_RETURN_VALUE:
            return self.neo4j_util.get_return_value_of_method(start_id=entity_id)
        if self.map_type == self.METHOD_2_FUNC_VERB:
            return self.neo4j_util.get_func_verb_of_method(start_id=entity_id)
        if self.map_type == self.CLASS_2_PARENT_PACKAGE:
            return self.neo4j_util.get_package_of_class(start_id=entity_id)
        if self.map_type == self.CLASS_2_PARENT_LIBRARY:
            return self.neo4j_util.get_library_of_class(start_id=entity_id)
        if self.map_type == self.CLASS_2_EXTENDS_CLASS:
            return self.neo4j_util.get_extends_class_of_class(start_id=entity_id)

        return self.UNMAP_ID

    def multi_map(self, entity_id: int) -> List[int]:
        if self.map_type == self.METHOD_2_PARENTS:
            class_of_method = self.neo4j_util.get_class_of_method(start_id=entity_id)
            package_of_method= self.neo4j_util.get_package_of_method(start_id=entity_id)
            lib_of_method = self.neo4j_util.get_library_of_method(start_id=entity_id)

            method_id = entity_id
            temp = [method_id, class_of_method, package_of_method, lib_of_method]
            final_result = []
            for t in temp:
                if t == self.UNMAP_ID:
                    continue
                final_result.append(t)
            return final_result
        if self.map_type == self.METHOD_2_NEIGHBOURS:
            parameters = self.neo4j_util.get_parameter_of_method(start_id=entity_id)
            return_value = self.neo4j_util.get_return_value_of_method(start_id=entity_id)
            class_of_method = self.neo4j_util.get_class_of_method(start_id=entity_id)
            method_id = entity_id
            temp = [method_id, class_of_method, return_value]+parameters
            final_result = []
            for t in temp:
                if t == self.UNMAP_ID:
                    continue
                final_result.append(t)
            return final_result
        if self.map_type == self.METHOD_2_NEIGHBOUR_CONCEPTS:
            parameter_concepts = self.neo4j_util.get_parameter_concepts_of_method(start_id=entity_id)
            parameter_type_concepts = self.neo4j_util.get_parameter_type_concepts_of_method(start_id=entity_id)
            return_value_type_concepts = self.neo4j_util.get_return_value_type_concepts_of_method(start_id=entity_id)
            class_concepts_of_method = self.neo4j_util.get_class_concepts_of_method(start_id=entity_id)
            functionalities_of_method = self.neo4j_util.get_functionality_of_method(start_id=entity_id)
            method_id = entity_id
            temp = [method_id] + parameter_concepts + parameter_type_concepts + return_value_type_concepts + class_concepts_of_method + functionalities_of_method
            final_result = []
            for t in temp:
                if t == self.UNMAP_ID:
                    continue
                final_result.append(t)
            return final_result
        if self.map_type == self.METHOD_2_NEIGHBOUR_WITH_CONCEPTS:
            parameters = self.neo4j_util.get_parameter_of_method(start_id=entity_id)
            return_value = self.neo4j_util.get_return_value_of_method(start_id=entity_id)
            class_of_method = self.neo4j_util.get_class_of_method(start_id=entity_id)
            concepts = self.neo4j_util.get_one_step_concept_of_method(start_id=entity_id)
            method_id = entity_id
            temp = [method_id, class_of_method, return_value]+parameters+concepts
            final_result = []
            for t in temp:
                if t == self.UNMAP_ID:
                    continue
                final_result.append(t)
            return final_result
        if self.map_type == self.METHOD_2_NEIGHBOUR_WITH_FUNCTIONALITIES:
            parameters = self.neo4j_util.get_parameter_of_method(start_id=entity_id)
            return_value = self.neo4j_util.get_return_value_of_method(start_id=entity_id)
            class_of_method = self.neo4j_util.get_class_of_method(start_id=entity_id)
            functionalities = self.neo4j_util.get_functionality_of_method(start_id=entity_id)
            method_id = entity_id
            temp = [method_id, class_of_method, return_value]+parameters+functionalities
            final_result = []
            for t in temp:
                if t == self.UNMAP_ID:
                    continue
                final_result.append(t)
            return final_result
        if self.map_type == self.METHOD_2_NEIGHBOUR_WITH_FUNC_VERBS:
            parameters = self.neo4j_util.get_parameter_of_method(start_id=entity_id)
            return_value = self.neo4j_util.get_return_value_of_method(start_id=entity_id)
            class_of_method = self.neo4j_util.get_class_of_method(start_id=entity_id)
            func_verb = self.neo4j_util.get_func_verb_of_method(start_id=entity_id)
            method_id = entity_id
            temp = [method_id, class_of_method, return_value, func_verb]+parameters
            final_result = []
            for t in temp:
                if t == self.UNMAP_ID:
                    continue
                final_result.append(t)
            return final_result

        if self.map_type == self.METHOD_2_NEIGHBOUR_WITH_FUNC_VERBS_FUNCTIONALITIES_CONCEPTS:
            parameters = self.neo4j_util.get_parameter_of_method(start_id=entity_id)
            return_value = self.neo4j_util.get_return_value_of_method(start_id=entity_id)
            class_of_method = self.neo4j_util.get_class_of_method(start_id=entity_id)
            func_verb = self.neo4j_util.get_func_verb_of_method(start_id=entity_id)
            functionalities = self.neo4j_util.get_functionality_of_method(start_id=entity_id)
            concepts = self.neo4j_util.get_one_step_concept_of_method(start_id=entity_id)
            method_id = entity_id
            temp = [method_id, class_of_method, return_value, func_verb]+parameters+functionalities+concepts
            final_result = []
            for t in temp:
                if t == self.UNMAP_ID:
                    continue
                final_result.append(t)
            return final_result
        if self.map_type == self.METHOD_2_PARAMETER_TYPES:
            temp = self.neo4j_util.get_parameter_type_of_method(start_id=entity_id)
            final_result = []
            for t in temp:
                if t == self.UNMAP_ID:
                    continue
                final_result.append(t)
            return final_result
        if self.map_type == self.METHOD_2_PARAMETERS:
            temp = self.neo4j_util.get_parameter_of_method(start_id=entity_id)
            final_result = []
            for t in temp:
                if t == self.UNMAP_ID:
                    continue
                final_result.append(t)
            return final_result
        if self.map_type == self.METHOD_2_CONCEPTS:
            temp = self.neo4j_util.get_one_step_concept_of_method(start_id=entity_id)
            final_result = []
            for t in temp:
                if t == self.UNMAP_ID:
                    continue
                final_result.append(t)
            return final_result
        if self.map_type == self.METHOD_2_FUNCTIONALITIES:
            temp = self.neo4j_util.get_functionality_of_method(start_id=entity_id)
            final_result = []
            for t in temp:
                if t == self.UNMAP_ID:
                    continue
                final_result.append(t)
            return final_result
        # if self.map_type == self.METHOD_2_FUNCTIONALITIES_CONCEPTS:
        #     temp = self.neo4j_util.get_functionality_of_method(start_id=entity_id)
        #     final_result = []
        #     for t in temp:
        #         if t == self.UNMAP_ID:
        #             continue
        #         final_result.append(t)
        #     return final_result
        if self.map_type == self.CLASS_2_PARENTS:
            package_of_class = self.neo4j_util.get_package_of_class(start_id=entity_id)
            lib_of_class = self.neo4j_util.get_library_of_class(start_id=entity_id)
            class_id = entity_id
            temp = [class_id, package_of_class, lib_of_class]
            final_result = []
            for t in temp:
                if t == self.UNMAP_ID:
                    continue
                final_result.append(t)
            return final_result
        if self.map_type == self.METHOD_2_RETURN_VALUE_TYPE_CONCEPTS:
            temp = self.neo4j_util.get_return_value_type_concepts_of_method(start_id=entity_id)
            final_result = []
            for t in temp:
                if t == self.UNMAP_ID:
                    continue
                final_result.append(t)
            return final_result
        if self.map_type == self.METHOD_2_CLASS_CONCEPTS:
            temp = self.neo4j_util.get_class_concepts_of_method(start_id=entity_id)
            final_result = []
            for t in temp:
                if t == self.UNMAP_ID:
                    continue
                final_result.append(t)
            return final_result
        if self.map_type == self.METHOD_2_PARAMETER_TYPE_CONCEPTS:
            temp = self.neo4j_util.get_parameter_type_concepts_of_method(start_id=entity_id)
            final_result = []
            for t in temp:
                if t == self.UNMAP_ID:
                    continue
                final_result.append(t)
            return final_result
        if self.map_type == self.METHOD_2_PARAMETER_CONCEPTS:
            temp = self.neo4j_util.get_parameter_concepts_of_method(start_id=entity_id)
            final_result = []
            for t in temp:
                if t == self.UNMAP_ID:
                    continue
                final_result.append(t)
            return final_result
        if self.map_type == self.CLASS_2_NEIGHBOURS:
            methods_of_class = self.neo4j_util.get_methods_of_class(start_id=entity_id)
            package_of_class = self.neo4j_util.get_package_of_class(start_id=entity_id)
            extends_class_of_class = self.neo4j_util.get_extends_class_of_class(start_id=entity_id)
            implements_interfaces_of_class = self.neo4j_util.get_implements_interfaces_of_class(start_id=entity_id)
            class_id = entity_id
            temp = [package_of_class, class_id, extends_class_of_class]+methods_of_class+implements_interfaces_of_class
            final_result = []
            for t in temp:
                if t == self.UNMAP_ID:
                    continue
                final_result.append(t)
            return final_result
        if self.map_type == self.CLASS_2_IMPLEMENTS_INTERFACES:
            temp = self.neo4j_util.get_implements_interfaces_of_class(start_id=entity_id)
            final_result = []
            for t in temp:
                if t == self.UNMAP_ID:
                    continue
                final_result.append(t)
            return final_result
        if self.map_type == self.CLASS_2_METHODS:
            temp = self.neo4j_util.get_methods_of_class(start_id=entity_id)
            final_result = []
            for t in temp:
                if t == self.UNMAP_ID:
                    continue
                final_result.append(t)
            return final_result
        return []

    def unify_map(self, entity_id) -> List[int]:
        if self.map_type in self.single_map_types:
            single_map = self.map(entity_id)
            if single_map == self.UNMAP_ID:
                return []
            return [single_map]
        if self.map_type in self.multi_map_types:
            return self.multi_map(entity_id)
        return []


class Node2VectorMapper:
    def __init__(self, milvus_util: MilvusUtil,
                 collection_name: str = "migration_small_test",
                 node2node_mapper=Node2NodeMapper()
                 ):
        self.node2node_mapper = node2node_mapper
        self.milvus_util = milvus_util
        self.collection_name = collection_name

    def map(self, entity_id) -> list:
        map_ids = self.node2node_mapper.unify_map(entity_id=entity_id)
        if len(map_ids) == 0:
            return []
        vectors = self.milvus_util.query_vectors_by_ids(ids=map_ids, collection_name=self.collection_name)
        if len(vectors) == 0:
            return []

        return self.milvus_util.average(vectors)

    def is_self_map(self):
        return self.node2node_mapper.is_self_map()
