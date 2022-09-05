import traceback
from functools import lru_cache
from typing import List

from py2neo import Graph
from py2neo.cypher import Cursor, Record


class Neo4jUtil:
    def __init__(self, graph: Graph = None):
        self.graph = graph

    @lru_cache(maxsize=10000)
    def get_library_id_by_node_id(self, node_id):
        start_node_info = self.get_node_by_id(node_id)
        start_library_id = start_node_info.get("library_id", -1)
        return start_library_id

    # @lru_cache(maxsize=10000)
    # def get_library_identity_by_node_id(self, node_id):
    #     start_node_info = self.get_node_by_id(node_id)
    #     start_library_id = start_node_info.get("library_id", -1)
    #     cypher = "match(l:library) where l.library_id = {} return id(n)".format(start_library_id)
    #
    #     return start_library_id

    @lru_cache(maxsize=10000)
    def get_node_by_id(self, id):
        cypher = f'MATCH (n) WHERE id(n)={id}  RETURN n'
        try:
            cursor: Cursor = self.graph.run(cypher=cypher)
            while cursor.forward():
                record: Record = cursor.current['n']
                node = {c: record.get(c) for c in record.keys()}
                if not node:
                    break
                data = node
                data['id'] = id
                return data
            return {}
        except Exception as e:
            traceback.print_exc()
            print("node for id %r not exist" % id)
            return {}

    def get_two_step_neighbour_by_id(self, start_id):
        cypher = "match (n) -[r] - (m) where id(n) = {} return id(n), n, type(r), id(m), m"
        cypher = cypher.format(start_id)
        out_re = {}
        data_list = self.graph.run(cypher).data()
        for data in data_list:
            n = dict(data["n"])
            n["id"] = data["id(n)"]
            m = dict(data["m"])
            m["id"] = data["id(m)"]
            r = data["type(r)"]
            m_id = m["id"]
            cypher = "match (n) -[r] - (m) where id(n) = {} return id(n), n, type(r), id(m), m"
            out_re["node_info"] = n
            cypher = cypher.format(m_id)
            in_re = {}
            data_list = self.graph.run(cypher).data()
            for data in data_list:
                if data["type(r)"] == r:
                    continue
                n = dict(data["n"])
                n["id"] = data["id(n)"]
                m = dict(data["m"])
                m["id"] = data["id(m)"]
                r = data["type(r)"]
                in_re["node_info"] = n
                if in_re.get("relations") is None:
                    in_re["relations"] = []
                in_re["relations"].append({"relation_name": r, "relation_node": m})

            if out_re.get("relations") is None:
                out_re["relations"] = []
            out_re["relations"].append({"relation_name": r, "relation_node": in_re})
        return out_re

    def get_neighbour_by_id(self, start_id):
        cypher = "match (n) -[r] - (m) where id(n) = {} return id(n), n, type(r), id(m), m"
        cypher = cypher.format(start_id)
        re = []
        data_list = self.graph.run(cypher).data()
        for data in data_list:
            m = dict(data["m"])
            m["id"] = data["id(m)"]
            r = data["type(r)"]
            re.append({"relation_name": r, "relation_node": m})
        return re

    def get_end_id_by_relation(self, start_id, relations: List[str]) -> List[int]:
        id_list = []
        cypher = 'match(n) - [:{}] -> (m) where id(n)={} return id(m)'.format(relations[0], start_id)

        if len(relations) == 3:
            cypher = 'match(n) - [:{}] -> () -[:{}] ->() - [:{}] -> (m) where id(n)={} return id(m)'.format(
                relations[0],
                relations[1],
                relations[2],
                start_id)
        if len(relations) == 2:
            cypher = 'match(n) - [:{}] -> () -[:{}] -> (m) where id(n)={} return id(m)'.format(relations[0],
                                                                                               relations[1], start_id)
        try:
            data = self.graph.run(cypher).data()
        except BaseException as e:
            print(e)
            data = []
        if len(data) > 0:
            for data_ in data:
                id_list.append(data_['id(m)'])
        return id_list

    def get_node_by_qualified_name(self, qualified_name):
        cypher = 'match(n:entity) where n.qualified_name = "{}" return n, id(n)'.format(qualified_name)
        try:
            cursor: Cursor = self.graph.run(cypher=cypher)
            while cursor.forward():
                record: Record = cursor.current['n']
                node = {c: record.get(c) for c in record.keys()}
                if not node:
                    break
                data = node
                data["id"] = cursor.current['id(n)']
                return data
            return {}
        except Exception as e:
            traceback.print_exc()
            print("node for id %r not exist" % id)
            return {}

    def get_out_relation_node(self, start_id):
        result = []
        try:
            cypher = "match(n:entity)-[r]-(m) where id(n) = {} return m, id(m), m.labels, r".format(start_id)
            data = self.graph.run(cypher).data()
            for data_ in data:
                r = data_['r']
                dic = {
                    "properties": dict(data_['m']),
                    "identity": data_['id(m)'],
                    "labels": data_['m.labels']
                }
                result.append((r, dic))
        except BaseException as e:
            print(e)
        return result


    def get_library_method_num(self):
        data_list = self.graph.run("match(n:library) return n").data()
        libraries = [dict(data["n"]) for data in data_list]
        print(libraries)

        for library in libraries:
            cypher = "match(n:method) where n.library_id={} return count(n)".format(library["library_id"])
            data = self.graph.run(cypher).data()
            library["method_num"] = data[0]["count(n)"]

        return libraries

    def post_neo4j(self, ids):
        result = []
        for id in ids:
            try:
                cypher = "match(n) where id(n) = {} return n, id(n), n.labels".format(id)
                data = self.graph.run(cypher).data()
                for data_ in data:
                    dic = {
                        "properties": dict(data_['n']),
                        "identity": data_['id(n)'],
                        "labels": data_['n.labels']
                    }
                    result.append(dic)
            except BaseException as e:
                print(e)
        return result

    @lru_cache(maxsize=10000)
    def get_return_value_type_of_method(self, start_id):
        ids = self.get_end_id_by_relation(start_id, ["has_return_value", "return_value_type_of"])
        if len(ids) == 0:
            return -1
        return ids[0]

    @lru_cache(maxsize=10000)
    def get_return_value_of_method(self, start_id):
        ids = self.get_end_id_by_relation(start_id, ["has_return_value"])
        if len(ids) == 0:
            return -1
        return ids[0]

    @lru_cache(maxsize=10000)
    def get_class_of_method(self, start_id):
        ids = self.get_end_id_by_relation(start_id, ["belong_to"])
        if len(ids) == 0:
            return -1
        return ids[0]

    @lru_cache(maxsize=10000)
    def get_package_of_method(self, start_id):
        ids = self.get_end_id_by_relation(start_id, ["belong_to", "exists_in"])
        if len(ids) == 0:
            return -1
        return ids[0]

    @lru_cache(maxsize=10000)
    def get_library_of_method(self, start_id):
        relations = ["belong_to", "exists_in", "include"]
        cypher = 'match(n:method) - [:{}] -> () -[:{}] ->(t:packages) <- [:{}] - (m:library) where id(n)={} return id(m)'.format(
            relations[0],
            relations[1],
            relations[2],
            start_id)
        ids = []
        try:
            data = self.graph.run(cypher).data()
            if len(data) > 0:
                for data_ in data:
                    ids.append(data_['id(m)'])
            if len(ids) == 0:
                return -1
            return ids[0]
        except BaseException as e:
            return -1

    @lru_cache(maxsize=10000)
    def get_parameter_type_of_method(self, start_id):
        ids = self.get_end_id_by_relation(start_id, ["has_parameter", "parameter_type_of"])
        if len(ids) == 0:
            return [-1]
        return ids

    @lru_cache(maxsize=10000)
    def get_functionality_of_method(self, start_id):
        ids = []
        relations = ["method_desc_include_functionality", "method_name_include_functionality"]
        cypher = "match(n:method) - [:{}|{}] -> (m) where id(n)={} return id(m)".format(relations[0], relations[1], start_id)
        try:
            data = self.graph.run(cypher).data()
            if len(data) > 0:
                for data_ in data:
                    ids.append(data_['id(m)'])
            if len(ids) == 0:
                return [-1]
            return ids
        except BaseException as e:
            return [-1]

    @lru_cache(maxsize=10000)
    def get_func_verb_of_method(self, start_id):
        ids = []
        relations = ["method_include_funcVerb"]
        cypher = "match(n:method) - [:{}] -> (m) where id(n)={} return id(m)".format(relations[0], start_id)
        try:
            data = self.graph.run(cypher).data()
            if len(data) > 0:
                for data_ in data:
                    ids.append(data_['id(m)'])
            if len(ids) == 0:
                return -1
            return ids[0]
        except BaseException as e:
            return -1

    @lru_cache(maxsize=10000)
    def get_class_concepts_of_method(self, start_id):
        ids = []
        relations = ["method_class_include_concept"]
        cypher = "match(n:method) - [:{}] -> (m) where id(n)={} return id(m)".format(relations[0], start_id)
        try:
            data = self.graph.run(cypher).data()
            if len(data) > 0:
                for data_ in data:
                    ids.append(data_['id(m)'])
            if len(ids) == 0:
                return [-1]
            return ids
        except BaseException as e:
            return [-1]

    @lru_cache(maxsize=10000)
    def get_return_value_type_concepts_of_method(self, start_id):
        ids = []
        relations = ["method_return_type_include_concept"]
        cypher = "match(n:method) - [:{}] -> (m) where id(n)={} return id(m)".format(relations[0], start_id)
        try:
            data = self.graph.run(cypher).data()
            if len(data) > 0:
                for data_ in data:
                    ids.append(data_['id(m)'])
            if len(ids) == 0:
                return [-1]
            return ids
        except BaseException as e:
            return [-1]

    @lru_cache(maxsize=10000)
    def get_parameter_type_concepts_of_method(self, start_id):
        ids = []
        relations = ["method_parameter_type_include_concept"]
        cypher = "match(n:method) - [:{}] -> (m) where id(n)={} return id(m)".format(relations[0], start_id)
        try:
            data = self.graph.run(cypher).data()
            if len(data) > 0:
                for data_ in data:
                    ids.append(data_['id(m)'])
            if len(ids) == 0:
                return [-1]
            return ids
        except BaseException as e:
            return [-1]

    @lru_cache(maxsize=10000)
    def get_parameter_concepts_of_method(self, start_id):
        ids = []
        relations = ["method_parameter_include_concept"]
        cypher = "match(n:method) - [:{}] -> (m) where id(n)={} return id(m)".format(relations[0], start_id)
        try:
            data = self.graph.run(cypher).data()
            if len(data) > 0:
                for data_ in data:
                    ids.append(data_['id(m)'])
            if len(ids) == 0:
                return [-1]
            return ids
        except BaseException as e:
            return [-1]

    @lru_cache(maxsize=10000)
    def get_parameter_of_method(self, start_id):
        ids = self.get_end_id_by_relation(start_id, ["has_parameter"])
        if len(ids) == 0:
            return [-1]
        return ids

    @lru_cache(maxsize=10000)
    def get_package_of_class(self, start_id):
        ids = self.get_end_id_by_relation(start_id, ["exists_in"])
        if len(ids) == 0:
            return -1
        return ids[0]

    @lru_cache(maxsize=10000)
    def get_library_of_class(self, start_id):
        relations = ["exists_in", "include"]
        cypher = 'match(n) -[:{}] ->(t:packages) <- [:{}] - (m:library) where id(n)={} return id(m)'.format(
            relations[0],
            relations[1],
            start_id)
        ids = []
        try:
            data = self.graph.run(cypher).data()
            if len(data) > 0:
                for data_ in data:
                    ids.append(data_['id(m)'])

            if len(ids) == 0:
                return -1
            return ids[0]
        except BaseException as e:
            return -1

    @lru_cache(maxsize=10000)
    def get_methods_of_class(self, start_id):
        relation = "belong_to"
        cypher = "match(m:method) -[:{}] ->(n:class)  where id(n)={} return id(m) ".format(relation, start_id)
        ids = []
        try:
            data = self.graph.run(cypher).data()
            if len(data) > 0:
                for data_ in data:
                    ids.append(data_['id(m)'])
            if len(ids) == 0:
                return [-1]
            return ids
        except BaseException as e:
            return [-1]

    @lru_cache(maxsize=10000)
    def get_extends_class_of_class(self, start_id):
        relation = "extends"
        cypher = 'match(n) -[:{}] ->(m) where id(n)={} return id(m)'.format( relation, start_id)
        ids = []
        try:
            data = self.graph.run(cypher).data()
            if len(data) > 0:
                for data_ in data:
                    ids.append(data_['id(m)'])

            if len(ids) == 0:
                return -1
            return ids[0]
        except BaseException as e:
            return -1

    @lru_cache(maxsize=10000)
    def get_implements_interfaces_of_class(self, start_id):
        relation = "implements"
        cypher = 'match(n) -[:{}] ->(m) where id(n)={} return id(m)'.format(relation, start_id)
        ids = []
        try:
            data = self.graph.run(cypher).data()
            if len(data) > 0:
                for data_ in data:
                    ids.append(data_['id(m)'])
            if len(ids) == 0:
                return [-1]
            return ids
        except BaseException as e:
            return [-1]

    @lru_cache(maxsize=10000)
    def get_concept_of_class(self, start_id):
        relation = "type_include_concept"
        cypher = 'match(n) -[:{}] ->(m:concept) where id(n)={} return id(m)'.format(relation, start_id)
        ids = []
        try:
            data = self.graph.run(cypher).data()
            if len(data) > 0:
                for data_ in data:
                    ids.append(data_['id(m)'])

            if len(ids) == 0:
                return -1
            return ids[0]
        except BaseException as e:
            return -1

    @lru_cache(maxsize=10000)
    def get_one_step_concept_of_method(self, start_id):
        # relation = "method_include_concept"
        cypher = 'match(n:method) -[] ->(m:concept) where id(n)={} return id(m)'.format(start_id)
        ids = []
        try:
            data = self.graph.run(cypher).data()
            if len(data) > 0:
                for data_ in data:
                    ids.append(data_['id(m)'])

            if len(ids) == 0:
                return [-1]
            return ids
        except BaseException as e:
            return [-1]

    @lru_cache(maxsize=10000)
    def get_concept_of_method(self, start_id):
        relation = "method_include_concept"
        cypher = 'match(n:method) -[:{}] ->(m:concept) where id(n)={} return id(m)'.format(relation, start_id)
        ids = []
        try:
            data = self.graph.run(cypher).data()
            if len(data) > 0:
                for data_ in data:
                    ids.append(data_['id(m)'])

            if len(ids) == 0:
                return -1
            return ids[0]
        except BaseException as e:
            return -1

