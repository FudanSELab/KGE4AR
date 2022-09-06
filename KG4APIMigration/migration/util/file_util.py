# !/usr/bin/env python
# -*- coding: utf-8 -*-
import json

class FileUtil:

    @staticmethod
    def load_data_list(file_path):
        index = file_path.rfind('.')
        file_type = file_path[index + 1:]
        if file_type == 'json':
            return FileUtil.load_data_list_from_json(file_path)
        if file_type == 'jl':
            return FileUtil.load_data_list_from_jl(file_path)
        if file_type == 'csv':
            return FileUtil.load_data_list_from_csv(file_path)


    @staticmethod
    def load_data_list_from_jl(jl_file_path):
        data_list = []
        with open(jl_file_path, encoding="utf-8") as file:
            line = file.readline()
            while line != "":
                try:
                    data_list.append(json.loads(line))
                except BaseException as e:
                    print(e)
                    print("error", line)
                line = file.readline()
        return data_list

    @staticmethod
    def load_data_list_from_json(json_file_path):
        with open(json_file_path, encoding="utf-8") as file:
            data_list = json.load(file)
        return data_list

    @staticmethod
    def load_data_list_from_csv(csv_file_path):
        data_list = []
        with open(csv_file_path) as f:
            lines = f.readlines()
            for line in lines:
                data_list.append(line.replace('\n', '').split(','))
        return data_list

    @staticmethod
    def write2jl(file, datalist):
        with open(file, mode='w') as f:
            for data in datalist:
                line = json.dumps(dict(data)) + "\n"
                f.write(line)

    @staticmethod
    def write2json(file, datalist):
        with open(file, "w") as f:
            json.dump(datalist, f, indent=4)

    @staticmethod
    def csv2list( files):
        new_lines = []
        for file in files:
            with open(file) as f:
                lines = f.readlines()
                for line in lines:
                    line = line.strip().split(",")
                    new_lines.append(line)
        return new_lines
