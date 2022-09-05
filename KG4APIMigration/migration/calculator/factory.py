from functools import lru_cache

from milvus import Milvus

from definitions import RemoteMilvus
from migration.calculator.constant import Constant
from migration.calculator.entity2vectormap_sim import Entity2VectorMappingMilvusSim, Entity2MaxVectorMappingMilvusSim
from migration.calculator.link_prediction_sim import ComplExLinkPredictionMilvusSim
from migration.converter.mapper import Node2NodeMapper
from migration.util.neo4j_util import Neo4jUtil
from migration.util.path_util import PathUtil


class MilvusSimFactory:
    def __init__(self, milvus: Milvus,
                 neo4j_util: Neo4jUtil,
                 collection_name=RemoteMilvus.MILVUS_TEST_COLLECTION,
                 partition_name=Constant.METHOD,
                 relation_embedding_path=PathUtil.complex_relation_file()
                 ):
        self.milvus_connection = milvus
        self.collection_name = collection_name
        self.neo4j_util = neo4j_util
        self.partition_name = partition_name
        self.relation_embedding_path = relation_embedding_path

    @lru_cache(maxsize=1)
    def self2self_node_mapper(self) -> Node2NodeMapper:
        start_node_mapper = Node2NodeMapper(
            map_type=Node2NodeMapper.SELF_MAP,
            neo4j_util=self.neo4j_util)
        return start_node_mapper

    def method2parent_class_node_mapper(self) -> Node2NodeMapper:
        start_node_mapper = Node2NodeMapper(
            map_type=Node2NodeMapper.METHOD_2_PARENT_CLASS,
            neo4j_util=self.neo4j_util)
        return start_node_mapper

    def method2parent_package_node_mapper(self) -> Node2NodeMapper:
        start_node_mapper = Node2NodeMapper(
            map_type=Node2NodeMapper.METHOD_2_PARENT_PACKAGE,
            neo4j_util=self.neo4j_util)
        return start_node_mapper

    def method2parent_library_node_mapper(self) -> Node2NodeMapper:
        start_node_mapper = Node2NodeMapper(
            map_type=Node2NodeMapper.METHOD_2_PARENT_LIBRARY,
            neo4j_util=self.neo4j_util)
        return start_node_mapper

    def method2return_value_type_node_mapper(self) -> Node2NodeMapper:
        start_node_mapper = Node2NodeMapper(
            map_type=Node2NodeMapper.METHOD_2_RETURN_VALUE_TYPE,
            neo4j_util=self.neo4j_util)
        return start_node_mapper

    def method2return_value_node_mapper(self) -> Node2NodeMapper:
        start_node_mapper = Node2NodeMapper(
            map_type=Node2NodeMapper.METHOD_2_RETURN_VALUE,
            neo4j_util=self.neo4j_util)
        return start_node_mapper

    def method2parents_node_mapper(self) -> Node2NodeMapper:
        start_node_mapper = Node2NodeMapper(
            map_type=Node2NodeMapper.METHOD_2_PARENTS,
            neo4j_util=self.neo4j_util)
        return start_node_mapper

    def method2neighbours_node_mapper(self) -> Node2NodeMapper:
        start_node_mapper = Node2NodeMapper(
            map_type=Node2NodeMapper.METHOD_2_NEIGHBOURS,
            neo4j_util=self.neo4j_util)
        return start_node_mapper

    def method2neighbour_concepts_node_mapper(self) -> Node2NodeMapper:
        start_node_mapper = Node2NodeMapper(
            map_type=Node2NodeMapper.METHOD_2_NEIGHBOUR_CONCEPTS,
            neo4j_util=self.neo4j_util)
        return start_node_mapper

    def method2neighbour_with_concepts_node_mapper(self) -> Node2NodeMapper:
        start_node_mapper = Node2NodeMapper(
            map_type=Node2NodeMapper.METHOD_2_NEIGHBOUR_WITH_CONCEPTS,
            neo4j_util=self.neo4j_util)
        return start_node_mapper

    def method2neighbour_with_func_verbs_node_mapper(self) -> Node2NodeMapper:
        start_node_mapper = Node2NodeMapper(
            map_type=Node2NodeMapper.METHOD_2_NEIGHBOUR_WITH_FUNC_VERBS,
            neo4j_util=self.neo4j_util)
        return start_node_mapper

    def method2neighbour_with_functionalities_node_mapper(self) -> Node2NodeMapper:
        start_node_mapper = Node2NodeMapper(
            map_type=Node2NodeMapper.METHOD_2_NEIGHBOUR_WITH_FUNCTIONALITIES,
            neo4j_util=self.neo4j_util)
        return start_node_mapper

    def method2neighbour_with_func_verbs_functionalities_concepts_node_mapper(self) -> Node2NodeMapper:
        start_node_mapper = Node2NodeMapper(
            map_type=Node2NodeMapper.METHOD_2_NEIGHBOUR_WITH_FUNC_VERBS_FUNCTIONALITIES_CONCEPTS,
            neo4j_util=self.neo4j_util)
        return start_node_mapper

    def method2parameter_types_node_mapper(self) -> Node2NodeMapper:
        start_node_mapper = Node2NodeMapper(
            map_type=Node2NodeMapper.METHOD_2_PARAMETER_TYPES,
            neo4j_util=self.neo4j_util)
        return start_node_mapper

    def method2parameters_node_mapper(self) -> Node2NodeMapper:
        start_node_mapper = Node2NodeMapper(
            map_type=Node2NodeMapper.METHOD_2_PARAMETERS,
            neo4j_util=self.neo4j_util)
        return start_node_mapper

    def method2concepts_node_mapper(self) -> Node2NodeMapper:
        start_node_mapper = Node2NodeMapper(
            map_type=Node2NodeMapper.METHOD_2_CONCEPTS,
            neo4j_util=self.neo4j_util)
        return start_node_mapper

    def method2functionalities_node_mapper(self) -> Node2NodeMapper:
        start_node_mapper = Node2NodeMapper(
            map_type=Node2NodeMapper.METHOD_2_FUNCTIONALITIES,
            neo4j_util=self.neo4j_util)
        return start_node_mapper

    def method2func_verb_node_mapper(self) -> Node2NodeMapper:
        start_node_mapper = Node2NodeMapper(
            map_type=Node2NodeMapper.METHOD_2_FUNC_VERB,
            neo4j_util=self.neo4j_util)
        return start_node_mapper

    def method2class_concepts_node_mapper(self) -> Node2NodeMapper:
        start_node_mapper = Node2NodeMapper(
            map_type=Node2NodeMapper.METHOD_2_CLASS_CONCEPTS,
            neo4j_util=self.neo4j_util)
        return start_node_mapper

    def method2parameter_type_concepts_node_mapper(self) -> Node2NodeMapper:
        start_node_mapper = Node2NodeMapper(
            map_type=Node2NodeMapper.METHOD_2_PARAMETER_TYPE_CONCEPTS,
            neo4j_util=self.neo4j_util)
        return start_node_mapper

    def method2parameter_concepts_node_mapper(self) -> Node2NodeMapper:
        start_node_mapper = Node2NodeMapper(
            map_type=Node2NodeMapper.METHOD_2_PARAMETER_CONCEPTS,
            neo4j_util=self.neo4j_util)
        return start_node_mapper

    def method2return_value_type_concepts_node_mapper(self) -> Node2NodeMapper:
        start_node_mapper = Node2NodeMapper(
            map_type=Node2NodeMapper.METHOD_2_RETURN_VALUE_TYPE_CONCEPTS,
            neo4j_util=self.neo4j_util)
        return start_node_mapper

    def class2parent_package_node_mapper(self) -> Node2NodeMapper:
        start_node_mapper = Node2NodeMapper(
            map_type=Node2NodeMapper.CLASS_2_PARENT_PACKAGE,
            neo4j_util=self.neo4j_util)
        return start_node_mapper

    def class2parent_library_node_mapper(self) -> Node2NodeMapper:
        start_node_mapper = Node2NodeMapper(
            map_type=Node2NodeMapper.CLASS_2_PARENT_LIBRARY,
            neo4j_util=self.neo4j_util)
        return start_node_mapper

    def class2parents_node_mapper(self) -> Node2NodeMapper:
        start_node_mapper = Node2NodeMapper(
            map_type=Node2NodeMapper.CLASS_2_PARENTS,
            neo4j_util=self.neo4j_util)
        return start_node_mapper

    def class2neighbours_node_mapper(self) -> Node2NodeMapper:
        start_node_mapper = Node2NodeMapper(
            map_type=Node2NodeMapper.CLASS_2_NEIGHBOURS,
            neo4j_util=self.neo4j_util)
        return start_node_mapper

    def class2methods_node_mapper(self) -> Node2NodeMapper:
        start_node_mapper = Node2NodeMapper(
            map_type=Node2NodeMapper.CLASS_2_METHODS,
            neo4j_util=self.neo4j_util)
        return start_node_mapper

    def class2extends_class_node_mapper(self) -> Node2NodeMapper:
        start_node_mapper = Node2NodeMapper(
            map_type=Node2NodeMapper.CLASS_2_EXTENDS_CLASS,
            neo4j_util=self.neo4j_util)
        return start_node_mapper

    def class2implements_interfaces_node_mapper(self) -> Node2NodeMapper:
        start_node_mapper = Node2NodeMapper(
            map_type=Node2NodeMapper.CLASS_2_IMPLEMENTS_INTERFACES,
            neo4j_util=self.neo4j_util)
        return start_node_mapper


    def method2method_milvus_sim(self) -> Entity2VectorMappingMilvusSim:
        entity_milvus_sim = Entity2VectorMappingMilvusSim(milvus_connection=self.milvus_connection,
                                                          collection_name=self.collection_name,
                                                          partition_name=Constant.METHOD,
                                                          start_node_mapper=self.self2self_node_mapper(),
                                                          end_node_mapper=self.self2self_node_mapper())

        return entity_milvus_sim

    def class2method_milvus_sim(self) -> Entity2VectorMappingMilvusSim:
        entity_milvus_sim = Entity2VectorMappingMilvusSim(milvus_connection=self.milvus_connection,
                                                          collection_name=self.collection_name,
                                                          partition_name=Constant.METHOD,
                                                          start_node_mapper=self.method2parent_class_node_mapper(),
                                                          end_node_mapper=self.self2self_node_mapper()
                                                          )
        return entity_milvus_sim

    def package2method_milvus_sim(self) -> Entity2VectorMappingMilvusSim:
        entity_milvus_sim = Entity2VectorMappingMilvusSim(milvus_connection=self.milvus_connection,
                                                          collection_name=self.collection_name,
                                                          partition_name=Constant.METHOD,
                                                          start_node_mapper=self.method2parent_package_node_mapper(),
                                                          end_node_mapper=self.self2self_node_mapper()
                                                          )
        return entity_milvus_sim

    def library2method_milvus_sim(self) -> Entity2VectorMappingMilvusSim:
        entity_milvus_sim = Entity2VectorMappingMilvusSim(milvus_connection=self.milvus_connection,
                                                          collection_name=self.collection_name,
                                                          partition_name=Constant.METHOD,
                                                          start_node_mapper=self.method2parent_library_node_mapper(),
                                                          end_node_mapper=self.self2self_node_mapper()
                                                          )
        return entity_milvus_sim

    def return_value_type2method_milvus_sim(self) -> Entity2VectorMappingMilvusSim:
        entity_milvus_sim = Entity2VectorMappingMilvusSim(milvus_connection=self.milvus_connection,
                                                          collection_name=self.collection_name,
                                                          partition_name=Constant.METHOD,
                                                          start_node_mapper=self.method2return_value_type_node_mapper(),
                                                          end_node_mapper=self.self2self_node_mapper()
                                                          )
        return entity_milvus_sim

    def return_value2method_milvus_sim(self) -> Entity2VectorMappingMilvusSim:
        entity_milvus_sim = Entity2VectorMappingMilvusSim(milvus_connection=self.milvus_connection,
                                                          collection_name=self.collection_name,
                                                          partition_name=Constant.METHOD,
                                                          start_node_mapper=self.method2return_value_node_mapper(),
                                                          end_node_mapper=self.self2self_node_mapper()
                                                          )
        return entity_milvus_sim

    def parents2method_milvus_sim(self) -> Entity2VectorMappingMilvusSim:
        entity_milvus_sim = Entity2VectorMappingMilvusSim(milvus_connection=self.milvus_connection,
                                                          collection_name=self.collection_name,
                                                          partition_name=Constant.METHOD,
                                                          start_node_mapper=self.method2parents_node_mapper(),
                                                          end_node_mapper=self.self2self_node_mapper()
                                                          )
        return entity_milvus_sim

    def neighbours2method_milvus_sim(self) -> Entity2VectorMappingMilvusSim:
        entity_milvus_sim = Entity2VectorMappingMilvusSim(milvus_connection=self.milvus_connection,
                                                          collection_name=self.collection_name,
                                                          partition_name=Constant.METHOD,
                                                          start_node_mapper=self.method2neighbours_node_mapper(),
                                                          end_node_mapper=self.self2self_node_mapper()
                                                          )
        return entity_milvus_sim

    def parameter_types2method_milvus_sim(self) -> Entity2VectorMappingMilvusSim:
        entity_milvus_sim = Entity2VectorMappingMilvusSim(milvus_connection=self.milvus_connection,
                                                          collection_name=self.collection_name,
                                                          partition_name=Constant.METHOD,
                                                          start_node_mapper=self.method2parameter_types_node_mapper(),
                                                          end_node_mapper=self.self2self_node_mapper()
                                                          )
        return entity_milvus_sim

    def parameters2method_milvus_sim(self) -> Entity2VectorMappingMilvusSim:
        entity_milvus_sim = Entity2VectorMappingMilvusSim(milvus_connection=self.milvus_connection,
                                                          collection_name=self.collection_name,
                                                          partition_name=Constant.METHOD,
                                                          start_node_mapper=self.method2parameters_node_mapper(),
                                                          end_node_mapper=self.self2self_node_mapper()
                                                          )
        return entity_milvus_sim


    def class2class_milvus_sim(self) -> Entity2VectorMappingMilvusSim:
        entity_milvus_sim = Entity2VectorMappingMilvusSim(milvus_connection=self.milvus_connection,
                                                          collection_name=self.collection_name,
                                                          partition_name=Constant.CLASS,
                                                          start_node_mapper=self.self2self_node_mapper(),
                                                          end_node_mapper=self.self2self_node_mapper())

        return entity_milvus_sim


    def package2class_milvus_sim(self) -> Entity2VectorMappingMilvusSim:
        entity_milvus_sim = Entity2VectorMappingMilvusSim(milvus_connection=self.milvus_connection,
                                                          collection_name=self.collection_name,
                                                          partition_name=Constant.CLASS,
                                                          start_node_mapper=self.class2parent_package_node_mapper(),
                                                          end_node_mapper=self.self2self_node_mapper()
                                                          )
        return entity_milvus_sim

    def library2class_milvus_sim(self) -> Entity2VectorMappingMilvusSim:
        entity_milvus_sim = Entity2VectorMappingMilvusSim(milvus_connection=self.milvus_connection,
                                                          collection_name=self.collection_name,
                                                          partition_name=Constant.CLASS,
                                                          start_node_mapper=self.class2parent_library_node_mapper(),
                                                          end_node_mapper=self.self2self_node_mapper()
                                                          )
        return entity_milvus_sim

    def methods2class_milvus_sim(self) -> Entity2VectorMappingMilvusSim:
        entity_milvus_sim = Entity2VectorMappingMilvusSim(milvus_connection=self.milvus_connection,
                                                          collection_name=self.collection_name,
                                                          partition_name=Constant.CLASS,
                                                          start_node_mapper=self.class2methods_node_mapper(),
                                                          end_node_mapper=self.self2self_node_mapper()
                                                          )
        return entity_milvus_sim

    def extends_class2class_milvus_sim(self) -> Entity2VectorMappingMilvusSim:
        entity_milvus_sim = Entity2VectorMappingMilvusSim(milvus_connection=self.milvus_connection,
                                                          collection_name=self.collection_name,
                                                          partition_name=Constant.CLASS,
                                                          start_node_mapper=self.class2extends_class_node_mapper(),
                                                          end_node_mapper=self.self2self_node_mapper()
                                                          )
        return entity_milvus_sim

    def implements_interfaces2class_milvus_sim(self) -> Entity2VectorMappingMilvusSim:
        entity_milvus_sim = Entity2VectorMappingMilvusSim(milvus_connection=self.milvus_connection,
                                                          collection_name=self.collection_name,
                                                          partition_name=Constant.CLASS,
                                                          start_node_mapper=self.class2implements_interfaces_node_mapper(),
                                                          end_node_mapper=self.self2self_node_mapper()
                                                          )
        return entity_milvus_sim

    def neighbours2class_milvus_sim(self) -> Entity2VectorMappingMilvusSim:
        entity_milvus_sim = Entity2VectorMappingMilvusSim(milvus_connection=self.milvus_connection,
                                                          collection_name=self.collection_name,
                                                          partition_name=Constant.CLASS,
                                                          start_node_mapper=self.class2neighbours_node_mapper(),
                                                          end_node_mapper=self.self2self_node_mapper()
                                                          )
        return entity_milvus_sim

    def parents2class_milvus_sim(self) -> Entity2VectorMappingMilvusSim:
        entity_milvus_sim = Entity2VectorMappingMilvusSim(milvus_connection=self.milvus_connection,
                                                          collection_name=self.collection_name,
                                                          partition_name=Constant.CLASS,
                                                          start_node_mapper=self.class2parents_node_mapper(),
                                                          end_node_mapper=self.self2self_node_mapper()
                                                          )
        return entity_milvus_sim


    def class_of_method2class_of_method_milvus_sim(self) -> Entity2VectorMappingMilvusSim:
        entity_milvus_sim = Entity2VectorMappingMilvusSim(milvus_connection=self.milvus_connection,
                                                          collection_name=self.collection_name,
                                                          partition_name=Constant.METHOD,
                                                          start_node_mapper=self.method2parent_class_node_mapper(),
                                                          end_node_mapper=self.method2parent_class_node_mapper()
                                                          )
        return entity_milvus_sim

    def package_of_method2package_of_method_milvus_sim(self) -> Entity2VectorMappingMilvusSim:
        entity_milvus_sim = Entity2VectorMappingMilvusSim(milvus_connection=self.milvus_connection,
                                                          collection_name=self.collection_name,
                                                          partition_name=Constant.METHOD,
                                                          start_node_mapper=self.method2parent_package_node_mapper(),
                                                          end_node_mapper=self.method2parent_package_node_mapper()
                                                          )
        return entity_milvus_sim

    def library_of_method2library_of_method_milvus_sim(self) -> Entity2VectorMappingMilvusSim:
        entity_milvus_sim = Entity2VectorMappingMilvusSim(milvus_connection=self.milvus_connection,
                                                          collection_name=self.collection_name,
                                                          partition_name=Constant.METHOD,
                                                          start_node_mapper=self.method2parent_library_node_mapper(),
                                                          end_node_mapper=self.method2parent_library_node_mapper()
                                                          )
        return entity_milvus_sim

    def return_value_type_of_method2return_value_type_of_method_milvus_sim(self) -> Entity2VectorMappingMilvusSim:
        entity_milvus_sim = Entity2VectorMappingMilvusSim(milvus_connection=self.milvus_connection,
                                                          collection_name=self.collection_name,
                                                          partition_name=Constant.METHOD,
                                                          start_node_mapper=self.method2return_value_type_node_mapper(),
                                                          end_node_mapper=self.method2return_value_type_node_mapper()
                                                          )
        return entity_milvus_sim

    def return_value_of_method2return_value_of_method_milvus_sim(self) -> Entity2VectorMappingMilvusSim:
        entity_milvus_sim = Entity2VectorMappingMilvusSim(milvus_connection=self.milvus_connection,
                                                          collection_name=self.collection_name,
                                                          partition_name=Constant.METHOD,
                                                          start_node_mapper=self.method2return_value_node_mapper(),
                                                          end_node_mapper=self.method2return_value_node_mapper()
                                                          )
        return entity_milvus_sim

    def parents_of_method2parents_of_method_milvus_sim(self) -> Entity2VectorMappingMilvusSim:
        entity_milvus_sim = Entity2VectorMappingMilvusSim(milvus_connection=self.milvus_connection,
                                                          collection_name=self.collection_name,
                                                          partition_name=Constant.METHOD,
                                                          start_node_mapper=self.method2parents_node_mapper(),
                                                          end_node_mapper=self.method2parents_node_mapper()
                                                          )
        return entity_milvus_sim

    def neighbors_of_method2neighbors_of_method_milvus_sim(self) -> Entity2VectorMappingMilvusSim:
        entity_milvus_sim = Entity2VectorMappingMilvusSim(milvus_connection=self.milvus_connection,
                                                          collection_name=self.collection_name,
                                                          partition_name=Constant.METHOD,
                                                          start_node_mapper=self.method2neighbours_node_mapper(),
                                                          end_node_mapper=self.method2neighbours_node_mapper()
                                                          )
        return entity_milvus_sim

    def neighbor_concepts_of_method2neighbor_concepts_of_method_milvus_sim(self) -> Entity2VectorMappingMilvusSim:
        entity_milvus_sim = Entity2VectorMappingMilvusSim(milvus_connection=self.milvus_connection,
                                                          collection_name=self.collection_name,
                                                          partition_name=Constant.METHOD,
                                                          start_node_mapper=self.method2neighbour_concepts_node_mapper(),
                                                          end_node_mapper=self.method2neighbour_concepts_node_mapper()
                                                          )
        return entity_milvus_sim

    def neighbor_with_concepts_of_method2neighbor_with_concepts_of_method_milvus_sim(self) -> Entity2VectorMappingMilvusSim:
        entity_milvus_sim = Entity2VectorMappingMilvusSim(milvus_connection=self.milvus_connection,
                                                          collection_name=self.collection_name,
                                                          partition_name=Constant.METHOD,
                                                          start_node_mapper=self.method2neighbour_with_concepts_node_mapper(),
                                                          end_node_mapper=self.method2neighbour_with_concepts_node_mapper()
                                                          )
        return entity_milvus_sim

    def neighbor_with_func_verbs_of_method2neighbor_with_func_verbs_of_method_milvus_sim(self) -> Entity2VectorMappingMilvusSim:
        entity_milvus_sim = Entity2VectorMappingMilvusSim(milvus_connection=self.milvus_connection,
                                                          collection_name=self.collection_name,
                                                          partition_name=Constant.METHOD,
                                                          start_node_mapper=self.method2neighbour_with_func_verbs_node_mapper(),
                                                          end_node_mapper=self.method2neighbour_with_func_verbs_node_mapper()
                                                          )
        return entity_milvus_sim

    def neighbor_with_functionalities_of_method2neighbor_with_functionalities_of_method_milvus_sim(self) -> Entity2VectorMappingMilvusSim:
        entity_milvus_sim = Entity2VectorMappingMilvusSim(milvus_connection=self.milvus_connection,
                                                          collection_name=self.collection_name,
                                                          partition_name=Constant.METHOD,
                                                          start_node_mapper=self.method2neighbour_with_functionalities_node_mapper(),
                                                          end_node_mapper=self.method2neighbour_with_functionalities_node_mapper()
                                                          )
        return entity_milvus_sim

    def neighbor_with_func_verbs_functionalities_concepts_of_method2neighbor_with_func_verbs_functionalities_concepts_of_method_milvus_sim(self) -> Entity2VectorMappingMilvusSim:
        entity_milvus_sim = Entity2VectorMappingMilvusSim(milvus_connection=self.milvus_connection,
                                                          collection_name=self.collection_name,
                                                          partition_name=Constant.METHOD,
                                                          start_node_mapper=self.method2neighbour_with_func_verbs_functionalities_concepts_node_mapper(),
                                                          end_node_mapper=self.method2neighbour_with_func_verbs_functionalities_concepts_node_mapper()
                                                          )
        return entity_milvus_sim


    def parameter_types_of_method2parameter_types_of_method_milvus_sim(self) -> Entity2VectorMappingMilvusSim:
        entity_milvus_sim = Entity2VectorMappingMilvusSim(milvus_connection=self.milvus_connection,
                                                          collection_name=self.collection_name,
                                                          partition_name=Constant.METHOD,
                                                          start_node_mapper=self.method2parameter_types_node_mapper(),
                                                          end_node_mapper=self.method2parameter_types_node_mapper()
                                                          )
        return entity_milvus_sim

    def parameters_of_method2parameters_of_method_milvus_sim(self) -> Entity2VectorMappingMilvusSim:
        entity_milvus_sim = Entity2VectorMappingMilvusSim(milvus_connection=self.milvus_connection,
                                                          collection_name=self.collection_name,
                                                          partition_name=Constant.METHOD,
                                                          start_node_mapper=self.method2parameters_node_mapper(),
                                                          end_node_mapper=self.method2parameters_node_mapper()
                                                          )
        return entity_milvus_sim

    def concepts_of_method2concepts_of_method_milvus_sim(self) -> Entity2VectorMappingMilvusSim:
        entity_milvus_sim = Entity2VectorMappingMilvusSim(milvus_connection=self.milvus_connection,
                                                          collection_name=self.collection_name,
                                                          partition_name=Constant.METHOD,
                                                          start_node_mapper=self.method2concepts_node_mapper(),
                                                          end_node_mapper=self.method2concepts_node_mapper()
                                                          )
        return entity_milvus_sim

    def functionalities_of_method2functionalities_of_method_milvus_sim(self) -> Entity2MaxVectorMappingMilvusSim:
        entity_milvus_sim = Entity2MaxVectorMappingMilvusSim(milvus_connection=self.milvus_connection,
                                                          collection_name=self.collection_name,
                                                          partition_name=Constant.METHOD,
                                                          start_node_mapper=self.method2functionalities_node_mapper(),
                                                          end_node_mapper=self.method2functionalities_node_mapper()
                                                          )
        return entity_milvus_sim

    def func_verb_of_method2func_verb_of_method_milvus_sim(self) -> Entity2VectorMappingMilvusSim:
        entity_milvus_sim = Entity2VectorMappingMilvusSim(milvus_connection=self.milvus_connection,
                                                          collection_name=self.collection_name,
                                                          partition_name=Constant.METHOD,
                                                          start_node_mapper=self.method2func_verb_node_mapper(),
                                                          end_node_mapper=self.method2func_verb_node_mapper()
                                                          )
        return entity_milvus_sim

    def class_concepts_of_method2class_concepts_of_method_milvus_sim(self) -> Entity2VectorMappingMilvusSim:
        entity_milvus_sim = Entity2VectorMappingMilvusSim(milvus_connection=self.milvus_connection,
                                                          collection_name=self.collection_name,
                                                          partition_name=Constant.METHOD,
                                                          start_node_mapper=self.method2class_concepts_node_mapper(),
                                                          end_node_mapper=self.method2class_concepts_node_mapper()
                                                          )
        return entity_milvus_sim

    def return_value_type_concepts_of_method2return_value_type_concepts_of_method_milvus_sim(self) -> Entity2VectorMappingMilvusSim:
        entity_milvus_sim = Entity2VectorMappingMilvusSim(milvus_connection=self.milvus_connection,
                                                          collection_name=self.collection_name,
                                                          partition_name=Constant.METHOD,
                                                          start_node_mapper=self.method2return_value_type_concepts_node_mapper(),
                                                          end_node_mapper=self.method2return_value_type_concepts_node_mapper()
                                                          )
        return entity_milvus_sim

    def parameter_type_concepts_of_method2parameter_type_concepts_of_method_milvus_sim(self) -> Entity2VectorMappingMilvusSim:
        entity_milvus_sim = Entity2VectorMappingMilvusSim(milvus_connection=self.milvus_connection,
                                                          collection_name=self.collection_name,
                                                          partition_name=Constant.METHOD,
                                                          start_node_mapper=self.method2parameter_type_concepts_node_mapper(),
                                                          end_node_mapper=self.method2parameter_type_concepts_node_mapper()
                                                          )
        return entity_milvus_sim

    def parameter_concepts_of_method2parameter_concepts_of_method_milvus_sim(self) -> Entity2VectorMappingMilvusSim:
        entity_milvus_sim = Entity2VectorMappingMilvusSim(milvus_connection=self.milvus_connection,
                                                          collection_name=self.collection_name,
                                                          partition_name=Constant.METHOD,
                                                          start_node_mapper=self.method2parameter_concepts_node_mapper(),
                                                          end_node_mapper=self.method2parameter_concepts_node_mapper()
                                                          )
        return entity_milvus_sim

    def method_A_belong_to_class_of_method_B(self) -> ComplExLinkPredictionMilvusSim:
        entity_milvus_sim = ComplExLinkPredictionMilvusSim(milvus_connection = self.milvus_connection,
                                                           collection_name=self.collection_name,
                                                           partition_name=Constant.METHOD,
                                                           start_node_mapper=self.self2self_node_mapper(),
                                                           end_node_mapper=self.method2parent_class_node_mapper(),
                                                           relation_type="belong_to",
                                                           relation_embedding_path=self.relation_embedding_path,
                                                           mode=ComplExLinkPredictionMilvusSim.MODE_START_NODE_AS_HEAD

                                                           )
        return entity_milvus_sim


    def method_B_belong_to_class_of_method_A(self) -> ComplExLinkPredictionMilvusSim:
        entity_milvus_sim = ComplExLinkPredictionMilvusSim(milvus_connection = self.milvus_connection,
                                                           collection_name=self.collection_name,
                                                           partition_name=Constant.METHOD,
                                                           start_node_mapper=self.method2parent_class_node_mapper(),
                                                           end_node_mapper=self.self2self_node_mapper(),
                                                           relation_type="belong_to",
                                                           relation_embedding_path=self.relation_embedding_path,
                                                           mode=ComplExLinkPredictionMilvusSim.MODE_START_NODE_AS_TAIL
                                                           )
        return entity_milvus_sim



    def methods_of_class2methods_of_class_milvus_sim(self) -> Entity2VectorMappingMilvusSim:
        entity_milvus_sim = Entity2VectorMappingMilvusSim(milvus_connection=self.milvus_connection,
                                                          collection_name=self.collection_name,
                                                          partition_name=Constant.CLASS,
                                                          start_node_mapper=self.class2methods_node_mapper(),
                                                          end_node_mapper=self.class2methods_node_mapper()
                                                          )
        return entity_milvus_sim

    def package_of_class2package_of_class_milvus_sim(self) -> Entity2VectorMappingMilvusSim:
        entity_milvus_sim = Entity2VectorMappingMilvusSim(milvus_connection=self.milvus_connection,
                                                          collection_name=self.collection_name,
                                                          partition_name=Constant.CLASS,
                                                          start_node_mapper=self.class2parent_package_node_mapper(),
                                                          end_node_mapper=self.class2parent_package_node_mapper()
                                                          )
        return entity_milvus_sim

    def library_of_class2library_of_class_milvus_sim(self) -> Entity2VectorMappingMilvusSim:
        entity_milvus_sim = Entity2VectorMappingMilvusSim(milvus_connection=self.milvus_connection,
                                                          collection_name=self.collection_name,
                                                          partition_name=Constant.CLASS,
                                                          start_node_mapper=self.class2parent_library_node_mapper(),
                                                          end_node_mapper=self.class2parent_library_node_mapper()
                                                          )
        return entity_milvus_sim


    def parents_of_class2parents_of_class_milvus_sim(self) -> Entity2VectorMappingMilvusSim:
        entity_milvus_sim = Entity2VectorMappingMilvusSim(milvus_connection=self.milvus_connection,
                                                          collection_name=self.collection_name,
                                                          partition_name=Constant.CLASS,
                                                          start_node_mapper=self.class2parents_node_mapper(),
                                                          end_node_mapper=self.class2parents_node_mapper()
                                                          )
        return entity_milvus_sim

    def neighbors_of_class2neighbors_of_class_milvus_sim(self) -> Entity2VectorMappingMilvusSim:
        entity_milvus_sim = Entity2VectorMappingMilvusSim(milvus_connection=self.milvus_connection,
                                                          collection_name=self.collection_name,
                                                          partition_name=Constant.CLASS,
                                                          start_node_mapper=self.class2neighbours_node_mapper(),
                                                          end_node_mapper=self.class2neighbours_node_mapper()
                                                          )
        return entity_milvus_sim

    def extends_class_of_class2extends_class_of_class_milvus_sim(self) -> Entity2VectorMappingMilvusSim:
        entity_milvus_sim = Entity2VectorMappingMilvusSim(milvus_connection=self.milvus_connection,
                                                          collection_name=self.collection_name,
                                                          partition_name=Constant.CLASS,
                                                          start_node_mapper=self.class2extends_class_node_mapper(),
                                                          end_node_mapper=self.class2extends_class_node_mapper()
                                                          )
        return entity_milvus_sim

    def implements_interfaces_of_class2implements_interfaces_of_class_milvus_sim(self) -> Entity2VectorMappingMilvusSim:
        entity_milvus_sim = Entity2VectorMappingMilvusSim(milvus_connection=self.milvus_connection,
                                                          collection_name=self.collection_name,
                                                          partition_name=Constant.METHOD,
                                                          start_node_mapper=self.class2implements_interfaces_node_mapper(),
                                                          end_node_mapper=self.class2implements_interfaces_node_mapper()
                                                          )
        return entity_milvus_sim

