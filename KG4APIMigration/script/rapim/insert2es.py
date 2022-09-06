# !/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
import os
from elasticsearch import Elasticsearch
from definitions import DATA_DIR
from migration.rapim.sentence_pipeline import SentencePipeline


type = "big"

sp = SentencePipeline()
es = Elasticsearch([{"host": "10.176.34.89", "port": 8200}])
es.indices.delete(index='api_migration_name_description_{}'.format(type), ignore=400)
es.indices.create(index='api_migration_name_description_{}'.format(type), ignore=400)
file = os.path.join(DATA_DIR, "icpc_saner", "id_name_desc_method_data_{}.csv".format(type))

name_description_body = []
count = 0
with open(file, encoding='utf-8') as f:
    f_csv = csv.reader(f)
    for line in f_csv:
        count = count + 1
        if count % 1000 == 0:
            print("process ", count)
            es.bulk(index="api_migration_name_description_{}".format(type), doc_type="_doc", body=name_description_body)
            name_description_body = []
        try:
            id = int(line[0])
            method_qualified_name = line[1]
            method_qualified_name = sp.special_characters_cleanup(method_qualified_name)
            method_qualified_name = sp.split_camel_case(method_qualified_name).lower()
            method_description = line[2]
            method_description = sp.special_characters_cleanup(method_description)
            method_description = sp.split_camel_case(method_description).lower()
            method_name_description = method_qualified_name + " " + method_description

            name_description_body.append(
                {"index": {"_index": "api_migration_name_description_{}".format(type), "_type": "_doc", "_id": id}}
            )
            name_description_body.append({
                "content": method_name_description,
                "id": id
            })
        except BaseException as e:
            print(e)


if name_description_body != []:
    es.bulk(index="api_migration_name_{}".format(type), doc_type="_doc", body=name_description_body)


print("insert es success")

