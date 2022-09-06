# !/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from py2neo import Graph
from definitions import DATA_DIR

class QueryDataGenerator():

    def __init__(self, graph):
        self.graph = graph

    def generate_id_from_neo4j(self, fileA, fileB, newfile):
        id_list_list = []

        # graph = Graph("neo4j://10.176.64.33:9123", user="neo4j", password="fdsefdse")
        with open(fileA) as fa:
            with open(fileB) as fb:
                linesA = fa.readlines()
                linesB = fb.readlines()
                for index, line_ in enumerate(linesA):
                    lines = [linesA[index], linesB[index]]
                    print("process", lines)
                    id_list = []
                    try:
                        for line in lines:

                                library_name, qualified_name = line.split("<L>")
                                library_name, qualified_name = library_name.strip(), qualified_name.strip()

                                if qualified_name != "no" and qualified_name != "many":
                                    package_name, class_name, method_name = self.get_package_class_method_name(qualified_name)
                                    id_temp_list = self.excute_cypher(self.graph, library_name, package_name, class_name, method_name, line.strip())
                                else:
                                    id_temp_list = self.excute_cypher(self.graph, library_name, None, None, None, line.strip())
                                for id in id_temp_list:
                                    id_list.append(id)
                        id_list_list.append(id_list)
                    except BaseException as e:
                        print(e, line)
                        id_list_list.append([str(-1), str(-1), str(-1), str(-1), str(-1), str(-1), str(-1), str(-1)])

        with open(newfile, "w") as f:
            for id_list in id_list_list:
                line = ",".join(id_list) + '\n'
                f.write(line)




    def excute_cypher(self, graph, library_name, package_name, class_name, method_name, all_name):
        id_list = [str(-1), str(-1), str(-1)]
        # cypher_list = [
        #     'match(n:library) where n.qualified_name = "{}"  and n.library_added_qualified_name contains ("{}") return id(n)',
        #     'match(n:packages) where n.qualified_name = "{}"  and n.library_added_qualified_name contains ("{}") return id(n)',
        #     'match(n:type) where n.qualified_name = "{}"  and n.library_added_qualified_name contains ("{}") return id(n)',
        #     'match(n:method) where n.qualified_name = "{}"  and n.library_added_qualified_name contains ("{}") return id(n)'
        # ]
        # name_list = [
        #     library_name,
        #     package_name,
        #     class_name,
        #     method_name
        # ]
        # for index, cypher in enumerate(cypher_list):
        #     if index == 3:
        #         if name_list[index] is not None and name_list[0] is not None:
        #             data = graph.run(cypher.format(name_list[index], name_list[0] + "<L>")).data()
        #             if len(data) > 0:
        #                 id_list.append(str(data[0]['id(n)']))
        #             else:
        #                 id_list.append(str(-1))
        #         else:
        #             id_list.append(str(-1))
        #     else:
        #         id_list.append(str(-1))
        cypher = 'match(n: method) where n.library_added_qualified_name="{}" return id(n)'.format(all_name)
        data = graph.run(cypher).data()

        if len(data) > 0:
            id_list.append(str(data[0]['id(n)']))
        else:
            id_list.append(str(-1))

        return id_list


    def get_package_class_method_name(self, qualified_name: str):

        dot_index = qualified_name.rfind(".")
        class_name = qualified_name[:dot_index]
        package_name = class_name
        while(True):
            dot_index = package_name.rfind(".")
            right = package_name[dot_index+1:]
            if not right.islower():
                package_name = package_name[:dot_index]

            else:
                break

        return package_name, class_name, qualified_name


    def clean_and_merge_data(self, old_files, new_file, new_file_name, data_type="method", split=3):
        position_a = 3
        position_b = 7
        if data_type == "method":
            position_a = 3
            position_b = 7
        if data_type == "class":
            position_a = 2
            position_b = 6

        clean_set = set([])
        clean_lines = []


        for file in old_files:
            with open(file) as f:
                lines = f.readlines()
                lines = [line.strip().split(',') for line in lines]
                try:
                    for line in lines:
                        if line[position_a] != '-1' and line[position_b] != '-1' and line[position_a] != -1 and line[position_b] != -1:
                            if str(line[position_a] + "_" + str(line[position_b])) not in clean_set and str(line[position_b] + "_" + str(line[position_a])) not in clean_set:
                                clean_set.add(str(line[position_a] + "_" + str(line[position_b])))
                                clean_lines.append(line)
                except BaseException as e:
                    print(e)
        clean_name_lines = []
        for line in clean_lines:
            name1 = line[3]
            name2 = line[7]
            temp = ["", "", "", "", "", "", "", ""]

            cypher = "match(n) where id(n) ={} return n.library_added_qualified_name".format(int(name1))
            data_list = graph.run(cypher).data()
            for data in data_list:
                temp[3] = dict(data)["n.library_added_qualified_name"]
            cypher = "match(n) where id(n) ={} return n.library_added_qualified_name".format(int(name2))
            data_list = graph.run(cypher).data()
            for data in data_list:
                temp[7] = dict(data)["n.library_added_qualified_name"]
            clean_name_lines.append(temp)
        with open(new_file, "w") as f:
            for line in clean_lines :
                line = ",".join(line) + '\n'
                f.write(line)

        with open(new_file_name, "w") as f:
            for line in clean_name_lines:
                line = "|".join(line) + '\n'
                f.write(line)

        num = len(clean_lines) // split
        for i in range(split):
            now_line = clean_lines[i*num:(i+1)*num]
            if i == split-1:
                now_line = clean_lines[i*num: len(clean_lines)]

            with open(str(i+1)+".csv", "w") as f:
                for line in now_line:
                    line = ",".join(line) + '\n'
                    f.write(line)



if __name__ == '__main__':
    type = "big"

    if type == "big":
        graph = Graph("neo4j://10.176.64.33:5687", user="neo4j", password="fdsefdse")
    else:
        graph = Graph("neo4j://10.176.64.33:9123", user="neo4j", password="fdsefdse")

    qdg = QueryDataGenerator(graph)
    # fileA = os.path.join(DATA_DIR, 'query_data', 'ICPC19MethodMigrationA.txt')
    # fileB = os.path.join(DATA_DIR, 'query_data', 'ICPC19MethodMigrationB.txt')
    # newfile = os.path.join(DATA_DIR, 'query_data', 'ICPC19MethodMigration_{}.csv'.format(type))
    # qdg.generate_id_from_neo4j(fileA, fileB, newfile)
    # print("generate file: ", "ICPC19MethodMigration_{}.csv".format(type))
    #
    # fileA = os.path.join(DATA_DIR, 'query_data', 'TSE19MethodMigrationA.txt')
    # fileB = os.path.join(DATA_DIR, 'query_data', 'TSE19MethodMigrationB.txt')
    # newfile = os.path.join(DATA_DIR, 'query_data', 'TSE19MethodMigration_{}.csv'.format(type))
    # qdg.generate_id_from_neo4j(fileA, fileB, newfile)
    # print("generate file: ", "TSE19MethodMigration_{}.csv".format(type))
    #
    # old_files = [os.path.join(DATA_DIR, 'query_data', 'ICPC19MethodMigration_{}.csv'.format(type))]
    # new_file = os.path.join(os.path.join(DATA_DIR, 'query_data', 'APIMigrationBenchmark_method_icpc_{}.csv'.format(type)))
    # new_file_name = os.path.join(os.path.join(DATA_DIR, 'query_data', 'APIMigrationBenchmark_method_icpc_name_{}.csv'.format(type)))
    # qdg.clean_and_merge_data(old_files, new_file, new_file_name, "method")
    # print("merge file: ", "APIMigrationBenchmark_method_icpc_{}.csv".format(type))
    # print("merge file: ", "APIMigrationBenchmark_method_icpc_name_{}.csv".format(type))
    #
    # old_files = [os.path.join(DATA_DIR, 'query_data', 'TSE19MethodMigration_{}.csv'.format(type))]
    # new_file = os.path.join(os.path.join(DATA_DIR, 'query_data', 'APIMigrationBenchmark_method_tse_{}.csv'.format(type)))
    # new_file_name = os.path.join(os.path.join(DATA_DIR, 'query_data', 'APIMigrationBenchmark_method_tse_name_{}.csv'.format(type)))
    # qdg.clean_and_merge_data(old_files, new_file, new_file_name, "method")
    # print("merge file: ", "APIMigrationBenchmark_method_tse_{}.csv".format(type))
    # print("merge file: ", "APIMigrationBenchmark_method_tse_name_{}.csv".format(type))



    old_files = [os.path.join(DATA_DIR, 'query_data', 'ICPC19MethodMigration_{}.csv'.format(type)),
                 os.path.join(DATA_DIR, 'query_data', 'TSE19MethodMigration_{}.csv'.format(type))]
    new_file = os.path.join(os.path.join(DATA_DIR, 'query_data', 'APIMigrationBenchmark_method_{}.csv'.format(type)))
    new_file_name = os.path.join(os.path.join(DATA_DIR, 'query_data', 'APIMigrationBenchmark_method_name_{}.csv'.format(type)))
    qdg.clean_and_merge_data(old_files, new_file, new_file_name, "method")
    print("merge file: ", "APIMigrationBenchmark_method_{}.csv".format(type))
    print("merge file: ", "APIMigrationBenchmark_method_name_{}.csv".format(type))










