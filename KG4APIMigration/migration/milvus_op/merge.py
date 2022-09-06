# !/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from definitions import DATA_DIR
from migration.util.file_util import FileUtil

type = "big"

file2num = {
    "packages_{}.jl".format(type): 1,
    "class_{}.jl".format(type): 2,
    "interface_{}.jl".format(type): 2,
    "method_{}.jl".format(type): 3,
    "library_{}.jl".format(type): 4,
    "parameter_{}.jl".format(type): 5,
    "return_value_{}.jl".format(type): 6,
    "concept_{}.jl".format(type): 7,
    "method_desc_include_functionality_{}.jl".format(type): 8,
    "method_name_include_functionality_{}.jl".format(type): 9,
    "func_verb_{}.jl".format(type): 10
}

re = {}

for k, v in file2num.items():
    print("process ", k)
    file = os.path.join(DATA_DIR, "milvus_data", k)
    data_list = FileUtil.load_data_list(file)
    for data in data_list:
        re[str(data["id"])] = v

file = os.path.join(DATA_DIR, "milvus_data", "filter_data_{}.json".format(type))

FileUtil.write2json(file, re)

