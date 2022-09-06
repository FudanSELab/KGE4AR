# !/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from definitions import OUTPUT_DIR
from migration.util.file_util import FileUtil


file = os.path.join(OUTPUT_DIR, "temp_result_1.jl")

index = [7, 20]

now_index = 0
data_list = FileUtil.load_data_list_from_jl(file)
for data in data_list:
    if data["position"] == -1:
        now_index = now_index + 1
        if now_index >= index[0] and now_index <= index[1]:
            print("=============================================================================================================")
            print({"library_id": data["start_node_info"]["library_id"], "name": data["start_node_info"]["library_added_qualified_name"]})
            print({"library_id": data["target_node_info"]["library_id"], "name": data["target_node_info"]["library_added_qualified_name"]})
            for ind, co in enumerate(data["combine_results"]):
                if ind >= 10:
                    break
                print({"library_id": co["node_info"]["library_id"], "name": co["node_info"]["library_added_qualified_name"]})
        elif now_index > index[1]:
            break

