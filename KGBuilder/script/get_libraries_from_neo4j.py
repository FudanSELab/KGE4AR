import json
import logging
import os

from py2neo import Graph
from py2neo.cypher import Cursor

from definitions import ThirdLibraryNeo4jConfigure


class Neo4jQuery:
    def __init__(self):
        self.graph = None
        # self.cypher_str = "MATCH (n:project {language:'$LANGUAGE$'})RETURN n Limit $MAX$"
        self.cypher_str = "MATCH (proj:project {language:'$LANGUAGE$'}) - [`has repository`]->(repo:repository) RETURN proj,repo.`stars count`  Limit $MAX$"

    def get_libraries(self, language_type_list, extract_max, extract_info_key, save_path, ip=None, username=None,
                      password=None):

        if not ip or username or not password:
            ip = ThirdLibraryNeo4jConfigure.IP
            username = ThirdLibraryNeo4jConfigure.USERNAME
            password = ThirdLibraryNeo4jConfigure.PASSWORD

        if not self.graph:
            self.graph = Graph(ip, auth=(username, password))

        if not os.path.exists(save_path):
            os.mkdir(save_path)

        for language_type in language_type_list:
            cypher_str = self.cypher_str.replace(r"$LANGUAGE$", language_type).replace(r"$MAX$", str(extract_max))
            info_list = []

            try:
                result_cursor: Cursor = self.graph.run(cypher_str)
                for record in result_cursor:
                    if not record[0]:
                        continue
                    proj = record[0]
                    proj_dict = {key: proj[key] for key in extract_info_key}

                    if record[1]:
                        proj_dict['stars'] = int(record[1])
                    else:
                        proj_dict['stars'] = 0

                    info_list.append(proj_dict)
                # 对结果按照star 数排序
                info_list.sort(key=lambda d: d['stars'], reverse=True)

                js_obj = json.dumps(info_list, indent=4)
                path_with_name = os.path.join(save_path, language_type) + '.json'
                with open(path_with_name, 'w') as fileObject:
                    fileObject.write(js_obj)
                    fileObject.close()

            except IndexError or TypeError:
                logging.warning("cypher {} is execute failed".format(cypher_str))
