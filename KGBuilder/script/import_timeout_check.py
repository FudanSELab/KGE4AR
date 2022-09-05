import threading
import sys

import py2neo
from py2neo import ClientError


class ImportTimeoutCheck(threading.Thread):
    def __init__(self, csv_importer, graph_accessor, graph_data, KG_CSV_DIR, lib_name, index):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.result = None
        self.error = None
        self.csv_importer = csv_importer
        self.graph_accessor = graph_accessor
        self.graph_data = graph_data
        self.KG_CSV_DIR = KG_CSV_DIR
        self.lib_name = lib_name
        self.index = index

        self.start()

    def run(self):
        try:
            self.result = self.csv_importer.run(self.graph_accessor, self.graph_data, self.KG_CSV_DIR, self.lib_name, self.index)
        #     重复节点异常
        except ClientError:
            self.error = sys.exc_info()
        # self.result = self.csv_importer.run(self.graph_accessor, self.graph_data, self.KG_CSV_DIR, self.lib_name, self.index)
