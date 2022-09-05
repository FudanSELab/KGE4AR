import os

# x=os.walk('/Users/imac/project/KGExport/data/parseResult')
from definitions import JAVA_REPOSITORIES_DIR, KG_DIR

# 获取当前目录的一级子目录
# print([x[1] for x in os.walk(JAVA_REPOSITORIES_DIR)][0])
# print([x[0] for x in os.walk(JAVA_REPOSITORIES_DIR)][1])

# print("ch-version:7.16"[0:"ch-version:7.16.0".find("-version:")])
# print(next(os.walk('/Users/imac/project/KGExport/data/parseResult'))[1])

# 获取资源
file_list = [x[0] for x in os.walk(KG_DIR)][1:]

for index, path in enumerate(file_list):
    sub_file_list = [x[2] for x in os.walk(path)][0]
    for j, sub_path in enumerate(sub_file_list):
        print(index, sub_path)
