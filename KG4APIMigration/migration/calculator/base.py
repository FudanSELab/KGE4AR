from abc import abstractmethod
from typing import List, Iterable
import numpy as np
from kgdt.utils import SaveLoad


class SimResult:

    def __init__(self, start_id, end_id, score, extra=None):
        if extra is None:
            extra = []
        self.start_id = start_id
        self.end_id = end_id
        self.score = score
        self.extra = extra

    def __repr__(self):
        return "<%r-%r:%r extra=%r>" % (self.start_id, self.end_id, self.score, self.extra)

    def __eq__(self, other):
        if other == None:
            return False
        if isinstance(other, SimResult) == False:
            return False
        if other.end_id == self.end_id:
            return True
        return False

    def __hash__(self):
        return hash(self.end_id)

    def get_score(self):
        return self.score

    def __lt__(self, other):
        return self.score < other.score


class SimResultCollection:

    def __init__(self, start_id):
        self.start_id = start_id
        self.sims = set([])
        self.id2score = {}

        self.__pos = 0

    def size(self):
        return len(self.sims)

    def get_end_ids(self):
        return self.id2score.keys()

    def add(self, sim_result: SimResult):
        if sim_result in self.sims:
            self.sims.remove(sim_result)
        self.sims.add(sim_result)
        self.id2score[sim_result.end_id] = sim_result.score

    def get_score(self, end_id):
        return self.id2score.get(end_id, 0)

    def add_all(self, sim_result_list: Iterable[SimResult]):
        for t in sim_result_list:
            self.add(t)

    def __len__(self):
        return len(self.sims)

    def __getitem__(self, index):
        return list(self.sims)[index]

    def __repr__(self):
        return "<SimResultCollection id=%r num=%r>" % (self.start_id, self.size())


class CombineSimResultCollection(SaveLoad):

    def __init__(self, start_id):
        self.start_id = start_id
        self.name2sim_collection = {}
        self.name2weight = {}
        self.name2filter_retention_num = {}

    def __repr__(self):
        name_weight_str = ",".join([name + ":" + str(weight) for name, weight in self.name2weight.items()])
        return "<CombineSimResultCollection id=%r %r>" % (self.start_id, name_weight_str)

    def get_all_names(self):
        return list(self.name2sim_collection.keys())

    def get_weight(self, name):
        return self.name2weight.get(name, 1.0)

    def get_all_weights(self):
        return [self.name2weight.get(name, 1.0) for name in self.get_all_names()]

    def add_sim_result(self, name: str, sim_result: SimResult):
        sim_collection: SimResultCollection = self.get_sim_collection(name)
        sim_collection.add(sim_result)
        self.name2weight[name] = 1

    def get_score(self, name, end_id):
        return self.get_sim_collection(name).get_score(end_id)

    def get_sim_collection(self, name):
        if name not in self.name2sim_collection:
            self.name2sim_collection[name] = SimResultCollection(self.start_id)
        return self.name2sim_collection[name]

    def get_all_scores(self, end_id):
        return [self.get_score(name=name, end_id=end_id) for name in self.get_all_names()]

    def get_combine_sim_result(self, name2weight: dict=None) -> List[SimResult]:
        all_end_ids = set([])
        if name2weight is not None:
            for k, v in name2weight.items():
                self.set_weight(k, v)
        for name, collection in self.name2sim_collection.items():
            all_end_ids.update(collection.get_end_ids())
        names = self.get_all_names()
        detail_scores_of_all_ids = [self.get_all_scores(end_id=end_id) for end_id in all_end_ids]
        weights = self.get_all_weights()
        try:
            # 将某个id的各个相似度汇总起来，进行加权和
            sum_score_of_all_ids = np.average(np.array(detail_scores_of_all_ids), axis=1, weights=weights)
            detail_scores_map_for_all_ids = [list(zip(names, detail_scores)) for detail_scores in detail_scores_of_all_ids]

            results = zip(all_end_ids, list(sum_score_of_all_ids), detail_scores_map_for_all_ids)
            sorted_results = sorted(results, key=lambda x: x[1], reverse=True)

            final_sim_results = [SimResult(start_id=self.start_id, end_id=combine_result[0], score=combine_result[1],
                                           extra=combine_result[2]) for
                                 combine_result in sorted_results]
            return final_sim_results
        except BaseException as e:
            print("CombineSimResultCollection", "get_combine_sim_result", e)
            return []


    def add_all_sim_result(self, name, sim_result_list: Iterable[SimResult]):
        for t in sim_result_list:
            self.add_sim_result(name, t)

    def set_weight(self, name, weight):
        if name in self.name2weight.keys():
            self.name2weight[name] = weight

    def set_filter_retention_num(self, name, filter_retention_num):
        if name in self.name2weight.keys():
            self.name2filter_retention_num[name] = filter_retention_num

    def update(self, combine_sim_result_collection):
        for name in combine_sim_result_collection.get_all_names():
            sim_result_collection = combine_sim_result_collection.get_sim_collection(name=name)
            self.add_all_sim_result(name=name, sim_result_list=sim_result_collection)
            self.set_weight(name=name, weight=combine_sim_result_collection.get_weight(name))
        self.name2filter_retention_num = combine_sim_result_collection.name2filter_retention_num


class MultiCombineSimResultCollection(SaveLoad):

    def __init__(self):
        self.id2name2sim_collection = {}

    def add(self, api_id, combine_sim_collection: CombineSimResultCollection):
        self.id2name2sim_collection[api_id] = combine_sim_collection

    def __len__(self):
        return len(self.id2name2sim_collection.keys())

    def __repr__(self):
        return "<MultiCombineSimResultCollection num=%d>" % len(self)

    def get_multi_data(self):
        all_score_map = {}
        ids = []
        multi_all_end_ids = []
        name2weight = {}
        try:
            for k, v in self.id2name2sim_collection.items():
                all_end_ids = set([])
                for name, collection in v.name2sim_collection.items():
                    all_end_ids.update(collection.get_end_ids())
                for id in all_end_ids:
                    all_score_map[str(k) + "_" + str(id)] = v.get_all_scores(end_id=id)
                ids.append(k)
                multi_all_end_ids.append(all_end_ids)
                name2weight = v.name2weight
            return multi_all_end_ids, all_score_map, ids, name2weight
        except BaseException as e:
            print(e, "MultiCombineSimResultCollection", "get_multi_data")
            return None, None, None, None

    def multi_get_combine_sim_result(self, multi_all_end_ids, all_score_map, ids, name2weight: dict = None):
        temp = {}
        name2weight_ = {}
        for k, v in self.id2name2sim_collection.items():
            csrc: CombineSimResultCollection = v
            name2weight_ = csrc.name2weight
            if name2weight is not None:
                name2weight_.update(name2weight)
            break
        weights = list(name2weight_.values())
        try:
            detail_scores_of_all_all_ids = list(all_score_map.values())
            sum_score_of_all_all_ids = np.average(np.array(detail_scores_of_all_all_ids), axis=1, weights=weights)
            index = 0
            new_map = {}
            for k, v in all_score_map.items():
                new_map[k] = sum_score_of_all_all_ids[index]
                index = index + 1
            for index, all_end_ids in enumerate(multi_all_end_ids):
                results = zip(all_end_ids, [new_map[str(ids[index] + "_" + str(i))] for i in all_end_ids])
                sorted_results = sorted(results, key=lambda x: x[1], reverse=True)
                final_sim_results = [combine_result[0] for combine_result in sorted_results]
                temp[ids[index]] = final_sim_results
            return temp
        except BaseException as e:
            print(e, "MultiCombineSimResultCollection", "multi_get_combine_sim_result")
            return temp


class SimCalculator:

    def __init__(self):
        pass

    def type(self):
        return str(self.__class__.__name__)

    def __repr__(self):
        return self.type()

    @abstractmethod
    def pair_sim(self, start_api_id, end_api_id) -> SimResult:
        return SimResult(start_api_id, end_api_id, 0.0)

    @abstractmethod
    def batch_sim(self, start_api_id, top_n=500) -> List[SimResult]:
        return []

    def batch_sim_collection(self, start_api_id, top_n=500) -> SimResultCollection:
        collection = SimResultCollection(start_id=start_api_id)
        collection.add_all(self.batch_sim(start_api_id=start_api_id, top_n=top_n))
        return collection

    def matrix_sim(self, start_api_ids, top_n=500) -> List[List[SimResult]]:
        return []
