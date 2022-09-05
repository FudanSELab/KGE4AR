import random


class DataSet:
    def __init__(self, data_type):
        self.query_data = [[]]
        self.position_a = 3
        self.position_b = 7
        self.data_type = data_type
        if data_type == "method":
            self.position_a = 3
            self.position_b = 7
        if data_type == "class":
            self.position_a = 2
            self.position_b = 6

    def load_from_text(self, path):
        pass

    def load_from_csv(self, path):
        with open(path) as f:
            lines = f.readlines()
            lines = [line.strip().split(',') for line in lines]
            clean_lines = []
            for line in lines:
                if line[self.position_a] != '-1' and line[self.position_b] != '-1' and line[self.position_a] != -1 and line[self.position_b] != -1:
                    clean_lines.append(line)
        self.query_data = clean_lines

    def load_from_jl(self, path):
        pass

    def save_to_jl(self, path):
        pass

    def split2ten(self):
        # random.shuffle(self.query_data)
        batch_size = len(self.query_data) // 10

        re = []
        try:
            for i in range(10):
                start = i * batch_size
                end = (i + 1) * batch_size
                test_data = self.query_data[start: end]
                train_data = self.query_data[0:start]
                train_data.extend(self.query_data[end: len(self.query_data)])
                test_data_set = DataSet(self.data_type)
                test_data_set.query_data = test_data
                train_data_set = DataSet(self.data_type)
                train_data_set.query_data = train_data
                re.append([test_data_set, train_data_set])

            return re
        except BaseException as e:
            print(e)
            return re


    def split(self, percent):
        # random.shuffle(self.query_data)
        train_size = int(len(self.query_data) * percent / 10)
        train_data = self.query_data[:train_size]
        test_data = self.query_data[train_size:]
        train_data_set = DataSet(self.data_type)
        train_data_set.query_data = train_data
        test_data_set = DataSet(self.data_type)
        test_data_set.query_data = test_data

        return train_data_set, test_data_set




