from typing import List

from migration.calculator.base import SimResult
from migration.util.db_util import DBUtil


class NodeFilter:
    EXTERNAL_CLASS_LIBRARY = 100000000


    def __init__(self, neo4j_util=DBUtil.get_test_api_kg_util()):
        self.neo4j_util = neo4j_util
        self.library_filter_map = {
            # com.fasterxml.jackson.core:jackson-core, com.fasterxml.jackson.core:jackson-databind
            # "404060": [404060, 651323],
            # "651323": [651323, 404060],
            # # org.slf4j:slf4j-simple, org.slf4j:slf4j-api, org.slf4j:slf4j-log4j12
            # "341980": [341980, 200000005, 200000004],
            # "200000005": [341980, 200000005, 200000004],
            # "200000004": [341980, 200000005, 200000004],

        }

        self.library_retention_map = {
        }

    def get_filter_lib_id(self, start_node_id) -> int:
        start_lib_id = self.neo4j_util.get_library_id_by_node_id(start_node_id)
        return start_lib_id

    def retention_for_icpc(self, target_api_id: int, id_list):
        retention_lib_id = self.get_filter_lib_id(start_node_id=target_api_id)
        retention_lib_ids = self.library_retention_map.get(str(retention_lib_id), [retention_lib_id])
        re = []
        for t in id_list:
            if self.is_valid(current_node_id=t, filter_lib_ids=retention_lib_ids) == True:
                continue
            re.append(t)
        return re

    def filter_for_icpc(self, start_api_id: int, id_list):

        filter_lib_id = self.get_filter_lib_id(start_node_id=start_api_id)
        filter_lib_ids = self.library_filter_map.get(str(filter_lib_id), [filter_lib_id])
        re = []
        for t in id_list:
            if self.is_valid(current_node_id=t, filter_lib_ids=filter_lib_ids) == False:
                continue
            re.append(t)
        return re

    def filter(self, start_api_id: int, combine_results: List[SimResult]) -> List[SimResult]:
        final_combine_results = []
        filter_lib_id = self.get_filter_lib_id(start_node_id=start_api_id)
        filter_lib_ids = self.library_filter_map.get(str(filter_lib_id), [filter_lib_id])
        for t in combine_results:

            if self.is_valid(current_node_id=t.end_id, filter_lib_ids=filter_lib_ids) == False:
                continue
            final_combine_results.append(t)
        return final_combine_results

    def retention(self, target_api_id: int, combine_results: List[SimResult]) -> List[SimResult]:
        final_combine_results = []
        retention_lib_id = self.get_filter_lib_id(start_node_id=target_api_id)
        retention_lib_ids = self.library_retention_map.get(str(retention_lib_id), [retention_lib_id])

        for t in combine_results:
            if self.is_valid(current_node_id=t.end_id, filter_lib_ids=retention_lib_ids) == True:
                continue
            final_combine_results.append(t)
        return final_combine_results


    def is_valid(self, current_node_id, filter_lib_ids):
        current_node_id_library_id = self.neo4j_util.get_library_id_by_node_id(current_node_id)
        if current_node_id_library_id == 100000000:
            return False
        if current_node_id_library_id in filter_lib_ids:
            return False
        else:
            return True

    def filter_method_in_one_class(self, id_list: [], num: int = 3):
        class_map = {}
        re = []
        for index, id in enumerate(id_list):
            class_id = self.neo4j_util.get_class_of_method(start_id=id)
            if class_id != -1:
                class_map[str(class_id)] = class_map.get(str(class_id), 0) + 1
                if class_map[str(class_id)] > num:
                    continue
            re.append(id)

        return re

    def filter_method_in_one_library(self, id_list: [], num: int = 100):
        library_map = {}
        re = []
        for index, id in enumerate(id_list):
            library_id = self.neo4j_util.get_library_of_method(start_id=id)
            if library_id != -1:
                library_map[str(library_id)] = library_map.get(str(library_id), 0) + 1
                if library_map[str(library_id)] > num:
                    continue
            re.append(id)

        return re




