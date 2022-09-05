import csv
import os

from script.neo4j import CSVGraphdataTranformer, BatchNeo4jImporter


# from kgdt.transfer.neo4j import CSVGraphdataTranformer


class CSVImporter:
    def __init__(self):
        self.translator = CSVGraphdataTranformer()

    # step1: graphdata2csv
    def graphdata2csv(self, graph_data, csv_folder, count):
        if not os.path.exists(csv_folder):
            os.mkdir(csv_folder)
        self.translator.graphdata2csv(csv_folder=csv_folder, graph=graph_data, only_one_relation_file=False,
                                      prefix=count, node_id_value_prefix=str(count))

    # 从csv获取所有node label
    def get_property_node_label(self, csv_file):
        return_property_map = {}
        return_labels = {}
        with open(csv_file, 'r', encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                row = dict(row)
                property_map = list(row.keys())
                for property_map_ in property_map:
                    return_property_map[property_map_] = property_map_

                return_labels = eval(row.get('labels'))
                break
        return return_property_map, return_labels

    # step2: 导入节点
    def node_csv2neo4j(self, csv_folder, lib_name, bni):
        for file in os.listdir(csv_folder):
            if file.find("$nodes$") != -1:
                full_file_name = os.path.join(csv_folder, file)
                return_property_map, return_labels = self.get_property_node_label(full_file_name)
                file_with_lib_name = os.path.join(lib_name, file)
                bni.batch_import_nodes_from_csv(1000, file_with_lib_name, return_labels, return_property_map)

    def get_realtion_label(self, csv_file):
        return_relation_label = {}
        with open(csv_file, 'r', encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                row = dict(row)
                return_relation_label = row.get('relationType')
                break
        return return_relation_label

    # step3: 导入关系
    def relation_csv2neo4j(self, csv_folder, lib_name, bni, count):

        for file in os.listdir(csv_folder):
            if file.find("$relations$") != -1:
                full_file_name = os.path.join(csv_folder, file)
                relation_label = self.get_realtion_label(full_file_name)
                match_nodes = [[['entity'], 'id', 'startId'],
                               [['entity'], 'id', 'endId']
                               ]
                ralations = [[1, relation_label, 2]]
                file_with_lib_name = os.path.join(lib_name, file)
                bni.batch_import_relations_from_csv(1000, file_with_lib_name, match_nodes, ralations)

    def run(self, graph_accessor, graph_data, csv_folder, lib_name, index):
        output_dir = os.path.join(csv_folder, lib_name)
        self.graphdata2csv(graph_data, output_dir, index)

        bni = BatchNeo4jImporter(graph_accessor)
        self.node_csv2neo4j(output_dir, lib_name, bni)
        self.relation_csv2neo4j(output_dir, lib_name, bni, index)
