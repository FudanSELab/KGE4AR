# !/usr/bin/env python
# -*- coding: utf-8 -*-
from queue import Queue
from threading import Thread
from py2neo import Graph


class Filter(Thread):

    def __init__(self, file_queue, thread_name):
        Thread.__init__(self, name=thread_name)
        self.file_queue = file_queue
        self.graph = Graph("neo4j://47.116.194.87:9210", user="neo4j", password="fdsefdse")

    def run(self):
        while self.file_queue.empty() == False:
            file_name = self.file_queue.get()
            self.filter2file(file_name)

    def filter(self, idendity):
        try:
            cypher = 'match(n) where id(n) = {} return n'.format(idendity)
            result = [i['n'] for i in self.graph.run(cypher).data()]
            result = result[0]
            labels = str(result.labels)
            if 'package' in labels:
                return 1
            if 'class' in labels:
                return 2
            if 'method' in labels:
                return 3
            if 'library' in labels:
                return 4
            if 'parameter' in labels:
                return 5
            if 'return_value' in labels:
                return 6
            if 'concept' in labels:
                return 7

            return 0
        except BaseException as e:
            print(e)
            print("error in filter")
            return 0

    def filter2file(self, path):
        index = path.find('.')
        left = path[:index] + "_new"
        right = path[index:]
        filter_file = left + right
        with open(filter_file, 'w') as fw:
            with open(path) as f:
                for line in f:
                    try:
                        line_list = line.split()
                        id = int(line_list[0])

                        re = self.filter(id)
                        line_list[0] = line_list[0] + "_" + str(re)
                        if re != 0:
                            fw.write(' '.join(line_list) + '\n')
                    except BaseException as e:
                        print(e)
                        print("error in filter2file")


if __name__ == '__main__':
    print("start")
    file_queue = Queue()
    file_name_list = []
    for i in range(49):
        file_name_list.append("entity_embeddings" + str(i+1) + ".tsv")
    for file_name in file_name_list:
        file_queue.put(file_name)
    print(file_queue)
    for index, file_name in enumerate(file_name_list):
        fil = Filter(file_queue, str(index))
        fil.start()