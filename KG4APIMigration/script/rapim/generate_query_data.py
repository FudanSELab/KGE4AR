# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-----------------------------------------
@Author: zz
@Email: 21212010059@m.fudan.edu.cn
@Created: 2022/08/08
------------------------------------------
@Modify: 2022/08/08
------------------------------------------
@Description:
"""
import os
from queue import Queue
from py2neo import Graph
from definitions import DATA_DIR, TestNEO4J, LargeNEO4J
from migration.rapim.neo4j_op import QueryData
from migration.util.file_util import FileUtil

type = "big"



cypher = "match(n:method) return min(id(n)), max(id(n))"
if type == "test":
    graph = Graph(TestNEO4J.URI, user=TestNEO4J.USERNAME, password=TestNEO4J.PASSWORD)
else:
    graph = Graph(LargeNEO4J.URI, user=LargeNEO4J.USERNAME, password=LargeNEO4J.PASSWORD)
data_list = graph.run(cypher).data()
data = dict(data_list[0])
start_end_queue = Queue()
min_id = data["min(id(n))"]
max_id = data["max(id(n))"]
print(min_id)
print(max_id)
all_num = max_id - min_id + 1
thread_num = 50
batch_size = all_num // thread_num
if all_num % thread_num != 0:
    thread_num = thread_num + 1

threads = []
for i in range(thread_num):
    start = min_id + i * batch_size
    end = min_id + (i + 1) * batch_size - 1
    if i == thread_num - 1:
        end = max_id
    start_end_queue.put([start, end])
for i in range(thread_num):
    qd = QueryData(start_end_queue, "thread" + str(i), graph)
    threads.append(qd)

for t in threads:
    t.start()
for t in threads:
    t.join()

li = []
for i in range(thread_num):
    file = os.path.join(DATA_DIR, "icpc_saner", "thread" + str(i) + ".json")
    data_list = FileUtil.load_data_list(file)
    li.append(data_list)

QueryData.merge(li, "all_data_{}.json".format(type))


